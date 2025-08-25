from .utils import *
import yaml
import json
import threading

try:
    import boto3
except:
    print('boto3 not installed, installing with pip ')
    from subprocess import call
    call('pip install boto3',shell = True)
    import boto3    
defaultconfig = {
    'wfield-preprocess': dict(
        submit = dict(
            instance_type =  'r5.16xlarge',
            analysis_extension = '.zip',
            userfolder = 'ChurchlandGroup',
            decompress_results = True),  # this will decompress the U matrix when downloading
        config = dict(block_height = 180,
                      block_width = 160,
                      frame_rate = 60,
                      max_components = 5,
                      num_sims = 64,
                      num_channels = 2,
                      overlapping = True,
                      window_length = 1000)), # 7200    
    'cshl-wfield-locanmf': {
        'submit':dict(
            instance_type =  'p3.2xlarge',
            userfolder = 'data',
            params_filename = 'config.yaml',
            areanames_filename = 'labels.json',
            atlas_filename = 'atlas.npy',
            brainmask_filename = 'brainmask.npy',
            temporal_data_filename = 'SVTcorr.npy',
            spatial_data_filename = 'U_atlas.npy'),
        'config' :{
            "maxrank": 3,
            "loc_thresh": 80,
            "min_pixels": 100,
            "r2_thresh": 0.99,
	    "maxiter_hals":20,
	    "maxiter_lambda":300,
	    "lambda_step":1.35,
	    "lambda_init":0.000001}}}

def ncaas_set_aws_keys(access_key,secret_key,region='us-east-1'):
    fname = pjoin(os.path.expanduser('~'),'.aws','credentials')
    cred = '''[default]
aws_access_key_id = {access_key}
aws_secret_access_key = {secret_key}
'''
    dirname = os.path.dirname(fname)
    if not os.path.isdir(dirname):
        os.makedirs(dirname)    
    with open(fname,'w') as fd:
        fd.write(cred.format(access_key=access_key,secret_key = secret_key))
    fname = pjoin(os.path.expanduser('~'),'.aws','config')
    if not region is None:
        conf = '''[default]
region={region}'''
        with open(fname,'w') as fd:
            fd.write(conf.format(region=region))

def ncaas_read_aws_keys():
    awsfolder = pjoin(os.path.expanduser('~'),'.aws')
    awscredfile = pjoin(awsfolder,'credentials')
    awsconfig = pjoin(awsfolder,'credentials')
    access_key = ''
    secret_key = ''
    region = 'us-east-1'
    if os.path.isfile(awscredfile):
        with open(awscredfile,'r') as fd:
            for ln in fd:
                if 'aws_access_key_id' in ln:
                    ln = ln.split('=')
                    if len(ln)>1:
                        access_key = ln[-1].strip(' ').strip('\n')
                if 'aws_secret_access_key' in ln:
                    ln = ln.split('=')
                    if len(ln)>1:
                        secret_key = ln[-1].strip(' ').strip('\n')
    if os.path.isfile(awsconfig):
        with open(awsconfig,'r') as fd:
            for ln in fd:
                if 'region' in ln:
                    ln = ln.split('=')
                    region = ln[-1].strip(' ')
    return dict(access_key = access_key,
                secret_key = secret_key,
                region = region)    

def ncaas_read_analysis_config(configname):
    if not os.path.exists(os.path.dirname(configname)):
        os.makedirs(os.path.dirname(configname))
    '''
    if os.path.exists(configname):
        with open(configname,'r') as f:
            config = json.load(f)
            # This is to delete a config from a previous version if there.
        if not list(defaultconfig.keys())[0] in config.keys():
            os.remove(configname)
            dirname = os.path.dirname(configname)
            qfile = pjoin(dirname,'ncaas_transfer_q.json')
            if os.path.isfile(qfile):
                os.remove(qfile)
    '''
    if not os.path.exists(configname):
        with open(configname,'w') as f:
            print('Creating config from defaults [{0}]'.format(configname))
            json.dump(defaultconfig, f,
                      indent = 4,
                      sort_keys = True)
    with open(configname,'r') as f:
        config = json.load(f)
        for k in config.keys():
            if k in defaultconfig.keys(): # Use default
                for j in defaultconfig[k].keys():
                    if not j in config[k].keys():
                        config[k][j] = defaultconfig[k][j]
    return config

def get_tree_path(items,root = ''):
    ''' Get the paths from a QTreeView item'''
    paths = []
    for item in items:
        level = 0
        index = item
        paths.append([index.data()])
        while index.parent().isValid():
            index = index.parent()
            level += 1
            paths[-1].append(index.data())
        for i,p in enumerate(paths[-1]):
            if p is None :
                paths[-1][i] = ''
        paths[-1] = '/'.join(paths[-1][::-1])
    return paths

def make_tree(item, tree):
    if len(item) == 1:
        if not item[0] == '':
            tree[item[0]] = item[0]
    else:
        head, tail = item[0], item[1:]
        tree.setdefault(head, {})
        make_tree(
            tail,
            tree[head])


def to_log(msg,logfile = None):
    if logfile is None:
        logfile = open(pjoin(
                     os.path.expanduser('~'),
                     '.wfield','ncaas_gui_log.txt'),'a')
    nmsg = '['+datetime.today().strftime('%y-%m-%d %H:%M:%S')+'] - ' + msg + '\n'
    logfile.seek(os.SEEK_END)
    logfile.write(nmsg)
    return nmsg

def tail(filename, nlines=100):
    """
    This needs work (should not read the whole file).
    """
    with open(filename,'r') as f:
        lines = f.readlines()
    if len(lines) > 100:
        lines = lines[-100:]
    return lines


##########
### S3 ###
##########
awsregions = ['us-east-2',
              'us-east-1',
              'us-west-1',
              'us-west-2',
              'af-south-1',
              'ap-east-1',
              'ap-south-1',
              'ap-northeast-3',
              'ap-northeast-2',
              'ap-southeast-1',
              'ap-southeast-2',
              'ap-northeast-1',
              'ca-central-1',
              'cn-north-1',
              'cn-northwest-1',
              'eu-central-1',
              'eu-west-1',
              'eu-west-2',
              'eu-south-1',
              'eu-west-3',
              'eu-north-1',
              'me-south-1',
              'sa-east-1']


def s3_connect():
    aws = ncaas_read_aws_keys()
    session = boto3.session.Session(aws_access_key_id = aws['access_key'],
                                    aws_secret_access_key = aws['secret_key'])
    return session.resource('s3'), session.client('s3')


from PyQt5.QtWidgets import QApplication # Keep the gui as responsive as possible..

def s3_ls(s3client, s3, bucketnames, folder ):
    files = []
    for bucketname in bucketnames:
        #bucket = s3.Bucket(bucketname)
        #t = bucket.objects.filter(Delimiter = '/',Prefix='{0}/'.format(folder))
        f = []
        files.extend(s3_ls_r(f,
                             s3client,
                             bucketname,
                             folder+'/'))
        
    return files

# recursive ls
def s3_ls_r(files,s3client,bucket,prefix):
    try:
        objlist = s3client.list_objects_v2(Bucket=bucket,
                                           Delimiter = '/',
                                           Prefix=prefix)
    except:
        return files
    if 'Contents' in objlist.keys():
        for obj in objlist['Contents']:
            QApplication.processEvents()
            files.append(bucket + '/'+obj['Key'])
    if 'CommonPrefixes' in objlist.keys():
        for obj in objlist['CommonPrefixes']:
            QApplication.processEvents()
            files.append(bucket + '/'+obj['Prefix'])
            s3_ls_r(files,s3client,bucket,obj['Prefix'])
    return files


from boto3.s3.transfer import TransferConfig
multipart_config = TransferConfig(multipart_threshold=1024*25,
                                  max_concurrency=12,
                                  multipart_chunksize=1024*25,
                                  use_threads=True)

class Upload(threading.Thread):
    def __init__(self,filepath,destination,bucket,s3):
        super(Upload,self).__init__()
        self.s3 = s3
        statinfo = os.stat(filepath)
        self.fsize = statinfo.st_size
        self.count = 0
        self.isrunning = False
        self.bucket = bucket
        self.filepath = filepath
        self.destination = destination
    def run(self):
        self.isrunning = True
        print('Running upload on {0} to {2}/{1}'.format(self.filepath,
                                                        self.destination,
                                                        self.bucket))
        def update(chunk):
            self.count += chunk
            self.isrunning = True
        bucket =self.s3.Bucket(self.bucket)
        bucket.upload_file(self.filepath,
                           self.destination,
                           Callback = update,
                           Config = multipart_config)
        self.isrunning = False


