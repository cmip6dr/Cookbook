class CMIP6_CVS(object):
    def __init__(self,cv_dir):
        self.experiment = json.load( open( '%s/%s' % (cv_dir,'CMIP6_experiment_id.json')))['experiment_id']
        self.model = json.load( open( '%s/%s' % (cv_dir,'CMIP6_source_id.json')))['source_id']

        
class MipPy(object):
    HOME = os.environ['HOME']
    SCRATCH_DEFAULT = HOME + '/.mippy'
    
    def _setup(self):
        self.scratch = SCRATCH_DEFAULT
        if not( os.path.isdir( self.scratch) ):
            os.mkdir( self.scratch )
    

class CMIP6_MipPy(MipPy):
    FIXED_TABLES = ['fx','Ofx']
    
    MIP_PATH = '/badc/cmip6/data/CMIP6'
    
    def __init__(self):
        self.cvs = CMIP6_CVS(self.HOME + '/work/CMIP6_CVs')

    def get_path(self,fn,version='latest'):
      bits = fn.rpartition('.')[0].split('_')
      var,table,model,experiment,variant,grid = bits[:6]
      if table not in self.FIXED_TABLES:
        tstart,tend = bits[6].split('-')
      else:
        tstart = tend = None
        
###
## TODO 
      mip = self.cvs.experiment[experiment]['activity_id'][0]
      inst = self.cvs.model[model]['institution_id'][0]
      print( mip, inst )
      if version == 'latest':
            dpath = '/'.join( [self.MIP_PATH,mip,inst,model,experiment,table,var,grid,version])
            version = os.readlink( dpath )
            is_latest = True
      else:
            dpath = '/'.join( [self.MIP_PATH,mip,inst,model,experiment,variant,table,var,grid,'latest'])
            latest_version = os.readlink( dpath )
            is_latest = latest_version == version 

      file_path = '/'.join( [self.MIP_PATH,mip,inst,model,experiment,variant,table,var,grid,version,fn])
      return file_path, is_latest
