"""
   Anonymising and shrinking netcdf files.
   The code will overwrite NetCDF global attributes using the template in setga1, substituting a dyanmically generated model name, and create new files (preserving CMIP style consistency between model name in the global attributes).
   The files are shrunk by extracting a small space-time slice using cdo commands.
"""
import glob, os, sys

class config(object):
  """Set some configuration values and check directories ... creating new as needed"""

  def __init__(self,idir='../files/nc_in/'):
    self.idir = idir
    self.odir1 = 'ncsubset'
    self.odir2 = 'cdl'
    self.start = 1
    self.end = 4

    for d in [self.odir1,self.odir2]:
      if not os.path.isdir(d):
        os.mkdir(d)


class base(object):
  """base class defining common utilities"""

  def __setFiles__(self,files,fpath,idir):
    if files == None:
      self.files = glob.glob( '%s/*.nc' % idir )
    elif fpath == 'rel':
      self.files = ['%s/%s' % (idir,x) for x in files]
    else:
      self.files = files

class step1(base):
  """Extract a subset of netcdf files.
  INPUTS
  ------
    cfg: an instance of the config class
    files[None]: a list of files
    fpath[rel]: (rel|abs) indicate whether file paths are relative to cfg.idir or absolute"""
  def __init__(self,cfg,files=None,fpath='rel'):
    self.cfg = cfg
    self.__setFiles__(files,fpath,cfg.idir)

  def run(self):
    kk = 0
    for f in self.files:
      kk += 1
      model = 'exAA%2.2i' % kk
      fn = f.split( '/' )[-1]
      assert fn[-3:] == '.nc', 'Only programmed for .nc files'
      if fn[-3:] == '.nc':
        fs0 = fn[:-3]
      bits = fs0.split('_')
      s = ''.join( open( 'setga1' ).readlines() ) % locals()
      oo = open( 'setga1p', 'w' )
      oo.write(s)
      oo.close()

      ##hurs_Amon_bcc-csm1-1_decadal1981_r1i1p1_198201-199112_box.cdl
      bits[2] = model
      fs = '_'.join( bits )
      if bits[0] == 'tnhus':
        os.popen( 'cdo setgatts,setga1p -seltimestep,1,2,3,4,5,6,7,8,9,10 %s %s/%s_slice.nc' % (f,self.cfg.odir1,fs) )
      else:
        os.popen( 'cdo setgatts,setga1p -seltimestep,1,2,3,4 -selindexbox,1,20,1,20 %s %s/%s_box.nc' % (f,self.cfg.odir1,fs) )
    

class step2(base):
  """Dumps netcdf files to cdl files
  INPUTS
  ------
    cfg: an instance of the config class
    files[None]: a list of files
    fpath[rel]: (rel|abs) indicate whether file paths are relative to cfg.idir or absolute"""
  def __init__(self,cfg,files=None,fpath='rel'):
    self.cfg = cfg
    self.__setFiles__(files,fpath,cfg.odir1)

  def run(self):
    for f in self.files:
      fn = f.split( '/' )[-1]
      assert fn[-3:] == '.nc', 'Only programmed for .nc files'
      if fn[-3:] == '.nc':
        fs = fn[:-3]
      os.popen( 'ncdump %s > %s/%s.cdl' % (f,self.cfg.odir2,fs) )
    

if __name__ == "__main__":
  if len(sys.argv) > 1:
    idir = sy.argv[1]
  else:
    idir = '../files/nc_in/'
  c = config(idir=idir)
  
  if c.start <= 1:
    s1 = step1(c)
    s1.run()
  
  if c.start <= 2:
    s2 = step2(c)
    s2.run()


