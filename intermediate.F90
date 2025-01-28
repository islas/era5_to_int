!
! f2py -c -m WPSUtils intermediate.F90
!
module intermediate

   implicit none

   ! Projection codes for proj_info structure:
   integer, public, parameter  :: PROJ_LATLON = 0
   integer, public, parameter  :: PROJ_LC = 1
   integer, public, parameter  :: PROJ_PS = 2
   integer, public, parameter  :: PROJ_PS_WGS84 = 102
   integer, public, parameter  :: PROJ_MERC = 3
   integer, public, parameter  :: PROJ_GAUSS = 4
   integer, public, parameter  :: PROJ_CYL = 5
   integer, public, parameter  :: PROJ_CASSINI = 6
   integer, public, parameter  :: PROJ_ALBERS_NAD83 = 105 
   integer, public, parameter  :: PROJ_ROTLL = 203

   integer :: output_unit
   character (len=64) :: met_out_filename
 

   contains


   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 
   ! Name: write_met_init
   !
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 
   function  write_met_init(prefix, datestr) result(istatus)
 
      implicit none
  
      ! Arguments
      character (len=*), intent(in) :: prefix
      character (len=*), intent(in) :: datestr

      ! Return value
      integer :: istatus
  
      ! Local variables
      integer :: io_status
      logical :: is_used

      istatus = 0
    
      !  1) BUILD FILENAME BASED ON TIME 
      met_out_filename = ' '
      write(met_out_filename, '(a)') trim(prefix)//':'//trim(datestr)
  
      !  2) OPEN FILE
      do output_unit=10,100
         inquire(unit=output_unit, opened=is_used)
         if (.not. is_used) exit
      end do 
      if (output_unit > 100) then
         write(0,*) 'In write_met_init(), couldn''t find an available Fortran unit.'
         return
      end if
      open(unit=output_unit, action='write', &
#ifdef __GNUC__
           convert='big_endian', &
#endif
           file=trim(met_out_filename), status='unknown', form='unformatted', iostat=io_status)

      if (io_status > 0) istatus = 1

   end function write_met_init
 
 
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 
   ! Name: write_next_met_field
   !
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 
   function write_next_met_field(version, nx, ny, iproj, xfcst, xlvl, &
                                   startlat, startlon, starti, startj, deltalat, deltalon, dx, dy, &
                                   xlonc, truelat1, truelat2, &
                                   earth_radius, is_wind_grid_rel, field, hdate, units, map_source, desc, &
                                   slab) result(istatus)
 
      implicit none
  
      ! Arguments
      integer, intent(in)                       :: version, nx, ny, iproj
      real, intent(in)                          :: xfcst, xlvl, startlat, startlon, starti, startj, &
                                                   deltalat, deltalon, dx, dy, xlonc, &
                                                   truelat1, truelat2, earth_radius
      real, dimension(:,:), intent(in)          :: slab
      logical, intent(in)                       :: is_wind_grid_rel
      character (len=9), intent(in)             :: field
      character (len=24), intent(in)            :: hdate
      character (len=25), intent(in)            :: units
      character (len=32), intent(in)            :: map_source
      character (len=46), intent(in)            :: desc

      ! Return value
      integer :: istatus
  
      ! Local variables
      character (len=8) :: startloc
      character (len=9) :: local_field
  
      istatus = 1
  
      !  1) WRITE FORMAT VERSION
      write(unit=output_unit) version

      local_field = field
      if (local_field == 'GHT      ') local_field = 'HGT      '

      if (version == 5) then

         if (starti == 1.0 .and. startj == 1.0) then
            startloc='SWCORNER'
         else
            startloc='CENTER  '
         end if

         ! Cylindrical equidistant
         if (iproj == PROJ_LATLON) then
            write(unit=output_unit) hdate,      &
                                    xfcst,      &
                                    map_source, &
                                    local_field,          &
                                    units,      &
                                    desc,       &
                                    xlvl,       &
                                    nx,         &
                                    ny,         &
                                    0
            write(unit=output_unit) startloc, &
                                    startlat, &
                                    startlon, &
                                    deltalat, &
                                    deltalon, &
                                    earth_radius

         ! Mercator
         else if (iproj == PROJ_MERC) then
            write(unit=output_unit) hdate,      &
                                    xfcst,      &
                                    map_source, &
                                    local_field,          &
                                    units,      &
                                    desc,       &
                                    xlvl,       &
                                    nx,         &
                                    ny,         &
                                    1
            write(unit=output_unit) startloc, &
                                    startlat, &
                                    startlon, &
                                    dx,       &
                                    dy,       &
                                    truelat1, &
                                    earth_radius

         ! Lambert conformal
         else if (iproj == PROJ_LC) then
            write(unit=output_unit) hdate,      &
                                    xfcst,      &
                                    map_source, &
                                    local_field,          &
                                    units,      &
                                    desc,       &
                                    xlvl,       &
                                    nx,         &
                                    ny,         &
                                    3
            write(unit=output_unit) startloc, &
                                    startlat, &
                                    startlon, &
                                    dx,       &
                                    dy,       &
                                    xlonc,    &
                                    truelat1, &
                                    truelat2, &
                                    earth_radius

         ! Gaussian
         else if (iproj == PROJ_GAUSS) then
            write(unit=output_unit) hdate,      &
                                    xfcst,      &
                                    map_source, &
                                    local_field,          &
                                    units,      &
                                    desc,       &
                                    xlvl,       &
                                    nx,         &
                                    ny,         &
                                    4
            write(unit=output_unit) startloc, &
                                    startlat, &
                                    startlon, &
                                    deltalat, &
                                    deltalon, &
                                    earth_radius

         ! Polar stereographic
         else if (iproj == PROJ_PS) then
            write(unit=output_unit) hdate,      &
                                    xfcst,      &
                                    map_source, &
                                    local_field,          &
                                    units,      &
                                    desc,       &
                                    xlvl,       &
                                    nx,         &
                                    ny,         &
                                    5
            write(unit=output_unit) startloc, &
                                    startlat, &
                                    startlon, &
                                    dx,       &
                                    dy,       &
                                    xlonc,    &
                                    truelat1, &
                                    earth_radius
     
         else
            write(0,*) 'Unrecognized projection code ', iproj, ' when reading from '//trim(met_out_filename)
     
         end if
  
         write(unit=output_unit) is_wind_grid_rel

         write(unit=output_unit) slab
      
         istatus = 0

      else
         write(0,*) 'Didn''t recognize format number ', version
      end if
  
   end function write_next_met_field
 
 
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 
   ! Name: write_met_close
   !
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 
   function write_met_close() result(istatus)
 
      implicit none

      integer :: istatus

      istatus = 0
  
      close(unit=output_unit)
      met_out_filename = 'UNINITIALIZED_FILENAME'
  
   end function write_met_close

end module intermediate
