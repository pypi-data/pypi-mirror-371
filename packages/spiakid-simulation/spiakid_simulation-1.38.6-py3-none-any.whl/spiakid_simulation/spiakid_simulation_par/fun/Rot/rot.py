import numpy as np
from scipy import interpolate
from astropy.coordinates import SkyCoord, EarthLocation, Angle, ICRS, FK5,AltAz
from astropy.timeseries import TimeSeries
from astropy.time import Time
from astropy import units as u


def Rotation(rotation, altguide, azguide, latitude, posx, posy, exptime, pxnbr, pxsize):
               
    guide_alt_az = [altguide,azguide]
    coo_star=[posx, posy]
    rot, evalt, alt_az_t, pos, star_ra_dec_t, alt_az_guide, ra_dec_guide = rot_with_pixel_scale(latitude, guide_alt_az, coo_star, exptime, pxsize, pxnbr)
   
    return(rot, evalt, alt_az_t, pos, star_ra_dec_t, alt_az_guide, ra_dec_guide)


def rot_with_pixel_scale(telescope_latitude_rad, 
        guide_star_altaz,
        offset_star_xy,
        duration_sec,
        pixel_scale_arcsec,
        pixel_nb):
    
    #   Constants
    observer_location = EarthLocation(lon=17.89 * u.deg, 
                                      lat=telescope_latitude_rad * u.rad, 
                                      height=2200 * u.m)
    times = np.linspace(0, duration_sec, duration_sec + 1)
    obs_time = Time("2020-01-01 20:00:00", scale = 'utc', location = observer_location)
    observation_times = obs_time + times * u.s
    captor_size_rad = pixel_scale_arcsec/3600 * pixel_nb *np.pi/180

    #   Guide coordinate
    alt_guide, az_guide = guide_star_altaz
    Xg, Yg, Zg = np.cos(alt_guide) * np.cos(az_guide), np.cos(alt_guide) * np.sin(az_guide), np.sin(alt_guide)
    guide_vector = np.array([Xg, Yg, Zg])

    captor_size_rad = pixel_scale_arcsec/3600 * pixel_nb *np.pi/180

    S1_alt = np.random.uniform(alt_guide-captor_size_rad/2, alt_guide+captor_size_rad/2)
    S1_az = np.random.uniform(az_guide-captor_size_rad/2, az_guide+captor_size_rad/2)
    X1, Y1, Z1 = np.cos(S1_alt) * np.cos(S1_az), np.cos(S1_alt) * np.sin(S1_az), np.sin(S1_alt)
    S1 = [X1, Y1, Z1]

    R = np.array([
                [np.sin(alt_guide)*np.cos(az_guide), np.sin(alt_guide)*np.sin(az_guide),-np.cos(alt_guide)],
                [-np.sin(az_guide), np.cos(az_guide), 0],
                [np.cos(alt_guide)*np.cos(az_guide), np.cos(alt_guide)*np.sin(az_guide),np.sin(alt_guide)]
            ])

    ra_dec_guide = []
    obs_time = Time("2020-01-01 20:00:00", scale = 'utc')
    repere_altaz = AltAz(location = observer_location, obstime =observation_times[0])
    coord_altaz_guide = SkyCoord(alt = alt_guide, az = az_guide,unit = 'rad', frame = repere_altaz)
    coord_equ_guide = coord_altaz_guide.transform_to("icrs")
    ra_dec_guide.append([coord_equ_guide.ra.value*np.pi/180, coord_equ_guide.dec.value*np.pi/180])

    ra_dec_star = []
    coord_altaz_star = SkyCoord(alt = S1_alt, az = S1_az, unit = 'rad', frame = repere_altaz)
    coord_equ_star = coord_altaz_star.transform_to("icrs")
    ra_dec_star.append([coord_equ_star.ra.value*np.pi/180, coord_equ_star.dec.value*np.pi/180])

    RAg, DECg = coord_equ_guide.ra.value*np.pi/180, coord_equ_guide.dec.value*np.pi/180
    RA, DEC = coord_equ_star.ra.value*np.pi/180, coord_equ_star.dec.value*np.pi/180



    altaz_guide = [] 
    altaz_star = []
    pos_star = []
    current_alt = []
    current_az = []
    current_az_star = []
    current_alt_star = []


    for i, t in enumerate(times):
            
            altaz = AltAz(location = observer_location, obstime = observation_times[i])
            
            coord_altaz = coord_equ_star.transform_to(altaz)
            coord_altaz_guide = coord_equ_guide.transform_to(altaz)

            current_alt = coord_altaz_guide.alt.value * np.pi/180
            current_az = coord_altaz_guide.az.value* np.pi/180
            current_alt_star = coord_altaz.alt.value * np.pi/180
            current_az_star = coord_altaz.az.value* np.pi/180

            altaz_guide.append([current_alt, current_az])
            altaz_star.append([current_alt_star, current_az_star])
    
            Xg, Yg, Zg = np.cos(current_az) * np.cos(current_alt), np.cos(current_alt) * np.sin(current_az), np.sin(current_alt)
            X1, Y1, Z1 = np.cos(current_alt_star) * np.cos(current_az_star), np.cos(current_alt_star) * np.sin(current_az_star), np.sin(current_alt_star)
            guide_vector = np.array([Xg, Yg, Zg])
            S1 = [X1, Y1, Z1]
            
            R = np.array([
                        [np.sin(current_alt)*np.cos(current_az), np.sin(current_alt)*np.sin(current_az),-np.cos(current_alt)],
                        [-np.sin(current_az), np.cos(current_az), 0],
                        [np.cos(current_alt)*np.cos(current_az), np.cos(current_alt)*np.sin(current_az),np.sin(current_alt)]
                        ])

            dx, dy, _ = R@(S1-guide_vector)
            pos_star.append([dy*180/np.pi * 3600/pixel_scale_arcsec, dx*180/np.pi * 3600/pixel_scale_arcsec])

 
    pos_star = np.array(pos_star)
    altaz_star = np.array(altaz_star)
    ev_alt = interpolate.interp1d(times, altaz_star[:,0])
    ev_x = interpolate.interp1d(times, pos_star[:,0])
    ev_y = interpolate.interp1d(times, pos_star[:,1])


    return ([ev_x, ev_y], ev_alt,altaz_star, pos_star, ra_dec_star, altaz_guide, ra_dec_guide)