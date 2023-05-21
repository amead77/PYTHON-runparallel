#######
#######
#######
####### runparallel.py -s c:\Users\adam\Downloads\8090 -d c:\Users\adam\Downloads\8090\outfiles -c 8 -f *.mp3 -p "filesweep.cmd"
#######
#######
#######

#>>> import psutil
#>>> psutil.cpu_count()
#4
#>>> p = psutil.Process()
#>>> # get
#>>> p.cpu_affinity()
#[0, 1, 2, 3]
#>>> # set; from now on, process will run on CPU #0 and #1 only
#>>> p.cpu_affinity([0, 1])
#>>> p.cpu_affinity()
#[0, 1]
#>>> # reset affinity against all eligible CPUs
#>>> p.cpu_affinity([])


import sys, argparse, os, glob, fnmatch, shutil, psutil, multiprocessing as mp, subprocess, time

#StartDir = ''



def ErrorArg(err):
    match err:
        case 0:
            print('Bye!')
            os.chdir(StartDir)    
        case 1:
            print('Source directory must be specified. Use -h for help.')
        case 2:
            print('Destination directory must be specified. Use -h for help.')
        case 3:
            print('Command to pass through must be specified. Use -h for help.')
        case 4:
            print('Source directory must exist! Use -h for help.')
        case 5:
            print('Destination directory must exist! Use -h for help.')
        case 6:
            print('Failed to change directory to the source! Use -h for help.')
        case 7:
            print('No files to work with using that file spec! Use -h for help.')
        case 8:
            print('no worries. Bye!')
            sys.exit(err)
        case 9:
            print('Can''t create sub directories! Check readonly/rights')
        case _:
            print('wtf?')
    print()
    print(r'Ex: runparallel.py -s c:\Users\adam\Downloads\8090 -d c:\Users\adam\Downloads\8090\outfiles -c 8 -f *.mp3 -p "filesweep.cmd"')
    print()
    print("note that this does not move files back to the source, so you'll need to do that manually. Also, programs like aacgain.exe need to be passed individual files, not directories. (see filesweep.cmd for an example)")
    sys.exit(err)
        


def FileLineCount(ff):
    count=0
    with open(ff,'rb') as tf:
        for line in tf:
            count = count + 1
    tf.close()
    return count
    
def RemoveTrailingSlash(s):
    #if s.startswith('/'):
    #    s = s[1:]
    if s.endswith('\\'):
        s = s[:-1]
    return s    

def CountFilesInDir(dir, fspec):
    #import fnmatch
    counter=len(fnmatch.filter(os.listdir(dir), fspec))
    return counter

def GetCopyMove():
    st=input('(M)ove, (C)opy, (S)kip or (E)xit:')
    st=st.upper()
    return st

def CreateDirs(DestDir, DirNum):
    if not os.path.isdir(DestDir+'\\'+str(DirNum)):
        os.mkdir(DestDir+'\\'+str(DirNum))
    if not os.path.isdir(DestDir+'\\'+str(DirNum)): ErrorArg(9)
    print('MkDir::'+str(DirNum))


    
def SplitFiles(CopyMove, SourceDir, DestDir, MaxFiles, FileSpec):
    DirNum=0
    counter=0
    for filen in glob.glob(FileSpec):
        counter=counter+1
        if ((counter >= MaxFiles) or (DirNum==0)):
            if DirNum==0: 
                DirNum=1
            else: 
                DirNum=DirNum+1
            CreateDirs(DestDir, DirNum)
            counter=0
        
        if CopyMove=='COPY':
            print('COPY::'+SourceDir+'\\'+filen+' -> '+DestDir+'\\'+str(DirNum)+'\\')
            shutil.copy2(SourceDir+'\\'+filen,DestDir+'\\'+str(DirNum)+'\\')
        elif CopyMove=='MOVE':
            print('MOVE::'+SourceDir+'\\'+filen+' -> '+DestDir+'\\'+str(DirNum)+'\\'+filen)
            shutil.move(SourceDir+'\\'+filen,DestDir+'\\'+str(DirNum)+'\\')
        else:
            print('wtf?')
            

def bytes2human(n):
    # http://code.activestate.com/recipes/578019
    # >>> bytes2human(10000)
    # '9.8K'
    # >>> bytes2human(100001221)
    # '95.4M'
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.1f%s' % (value, s)
    return "%sB" % n
    

def spawn(MaxCores, PassThru, DestDir):
	for cpu in range(1,MaxCores+1):

		os.chdir(DestDir+'\\'+str(cpu))
		run_child(cpu, PassThru)
            
def run_child(Affinity, PassThru):
    cpu=Affinity
    match cpu:
        case 1: Affinity=1
        case 2: Affinity=2
        case 3: Affinity=4
        case 4: Affinity=8
        case 5: Affinity=10
        case 6: Affinity=20
        case 7: Affinity=40
        case 8: Affinity=80
        case 9: Affinity=100
        case 10: Affinity=200
        case 11: Affinity=400
        case 12: Affinity=800
        case 13: Affinity=1000
        case 14: Affinity=2000
        case 15: Affinity=4000
        case 16: Affinity=8000
        case _: Affinity=1

    cmd='start "cpu core {} -- {}" /affinity {} {}'.format(cpu, Affinity, Affinity, PassThru)
    os.popen(cmd)
	#os.popen('start "cpu core '+str(cpu)+'-'+str(Affinity)+'"'+' /affinity '+str(Affinity)+' '+PassThru)
    
def dtime(cmd):
    cmd = float(cmd/1000)
    time.sleep(cmd)
    return
    
def main():
    global StartDir
    StartDir=RemoveTrailingSlash(os.getcwd())
    print('Current directory:   ', StartDir)
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--SourceDir', action='store', help='Source Directory', default='')
    parser.add_argument('-d', '--DestDir', action='store', help='Destination Directory', default='')
    parser.add_argument('-c', '--MaxCores', action='store', type=int, help='Maximum cores/directory splits to use/make (defaults to 2)', default=2)
    parser.add_argument('-f', '--FileSpec', action='store', help='Filespec, ex: *.mp3 (defaults to *.*)', default='*.*')
    parser.add_argument('-p', '--PassThru', dest='PassThru', action='store', help='parameters to pass to CMD', default='')
    args = parser.parse_args()
    
    if args.SourceDir=='': ErrorArg(1)
    if args.DestDir=='': ErrorArg(2)
    if args.PassThru=='': ErrorArg(3)
    
    args.SourceDir=RemoveTrailingSlash(args.SourceDir)
    args.DestDir=RemoveTrailingSlash(args.DestDir)

    ActualCores=psutil.cpu_count()
    if args.MaxCores>ActualCores: args.MaxCores=ActualCores
    print('Actuals CPUs/Cores:  ', ActualCores)
    print('Max Cores to use:    ', args.MaxCores)
    print('Memory Free:         ',bytes2human(psutil.virtual_memory().free))
    print('Source:              ', args.SourceDir)
    print('Destination:         ', args.DestDir)
    print('FileSpec:            ', args.FileSpec)
    print('PassThru:            ', args.PassThru)
    
    if not os.path.isdir(args.SourceDir): ErrorArg(4)
    if not os.path.isdir(args.DestDir): ErrorArg(5)
    
    
     
    FileCount = CountFilesInDir(args.SourceDir, args.FileSpec)
    print('Matching files here: ', FileCount)
    if FileCount == 0: ErrorArg(7)
    MaxFilesPerDir=int(FileCount/args.MaxCores)+1
    print('Splitting into:      ',MaxFilesPerDir)
    
    if StartDir.upper() != args.SourceDir.upper():
        print('ChDir to ',args.SourceDir)
        os.chdir(args.SourceDir)
        if os.getcwd().upper() != args.SourceDir.upper(): ErrorArg(6)
        print('Now in ', os.getcwd())
    
    CopyMove=''
    while not CopyMove in ['C','M','S','E']:
        CopyMove=GetCopyMove()
    
    if CopyMove=='E': 
        ErrorArg(8)
    elif CopyMove=='C':
        print('Copy Files')
        SplitFiles('COPY', args.SourceDir, args.DestDir, MaxFilesPerDir, args.FileSpec)
    elif CopyMove=='M':
        print('Move Files')
        SplitFiles('MOVE', args.SourceDir, args.DestDir, MaxFilesPerDir, args.FileSpec)
    elif CopyMove=='S':
        print('Skipping this bit')
    
    print('waiting 2 secs before continuing ..')
    dtime(2000)
    spawn(args.MaxCores, args.PassThru, args.DestDir)
    
    
    
    
    
    ErrorArg(0)
    #should never reach here
    sys.exit(255)
  
    
if __name__ == '__main__':
    main()   
    
    