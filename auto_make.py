#!/bin/env python
# coding:utf-8

import os, shutil, re


DirName = os.getcwd()
CurrentFile = os.listdir(DirName)
OriFile = ['bin', 'cfg_module.cfg', 'Dockerfile', 'Dockerfile_extra', 'auto_make.py', 'mmp_init', 'stop-ats', 'md5_dep.exe', 'auto_make.pyc']
FileList = ['ch', 'dx', 'gz', 'hf']
FileListExtra = ['ch', 'dx', 'gz', 'hf', 'yd']

def RmSpcTree(dirname, spctreename='.svn'):
	'''
	遍历文件夹，删除指定名称的文件夹
	这里用来清除.svn文件夹
	'''
	
	for tmpname in os.walk(dirname):
		if spctreename in tmpname[1]:
			print os.path.join(tmpname[0], spctreename)
			print "%s delete compelet"  %spctreename
			shutil.rmtree(os.path.join(tmpname[0], spctreename))


def FileNumCheck():
	'''
	校验文件和文件夹数量，返回文件路径名称和执行文件名称
	用于后期修改模板文件对应的参数
	'''
	[ CurrentFile.remove(element) for element in OriFile ]

	if len(CurrentFile) != 1:
		print "file num wrong"
		exit(1)
	
	pathname = CurrentFile[0]
	bindir = os.path.join(pathname, 'bin')
	pattern = re.compile(r'ats')
	
	#检查有没有bin目录，没有bin目录的非标准组件，无法用脚本处理
	if not os.path.isdir(bindir):
		print "not bin dir in %s" %pathname
		exit(1)
	
	#输入组件名
	comname = raw_input("firstly, pls insert comname: ")
	
	#检查有没有对应的执行文件，如果与目录名不一致会查询出带有ats字样的文件，提示手动输入执行文件名	
	if not os.path.isfile(os.path.join(bindir, pathname)):
		print "exec FileName not equal pathname"
		print "FileName with ats found in bin dir, pls select: "
		for str in os.listdir(bindir):
			match = pattern.match(str)
			if match:
				print str
		exefilename = raw_input("input exefilename: ")
	else:
		exefilename = pathname
	
	#返回目录名,组件名,执行文件名供后续修改dockerfile使用
	return pathname,comname,exefilename


def mkDir(*filelist):
	'''
	批量建立文件夹
	'''
	[ os.mkdir(str) for str in filelist ]


def ReplaceStr(filename, *namefield):
	'''
	替换模板文件中的特定字符串: engine_name, com_name, exefilename
	'''
	tmp_filename = ''.join([filename, '_tmp'])
	tmp_file = open(tmp_filename, 'w')
	with open(filename) as basefile:
	    for line in basefile:
			line = line.replace('{engine_name}', namefield[0])
			line = line.replace('{com_name}', namefield[1])
			line = line.replace('{exe_name}', namefield[2])
			tmp_file.write(line)
	tmp_file.close()
	
	
def MvFile(atsdir, bindir='bin'):
	'''
	移动bin下的文件到引擎文件夹下
	'''
	for filename in os.listdir(bindir):
		bin_filename = os.path.join(bindir, filename)
		abs_filename = os.path.join(atsdir, bindir, filename)
		shutil.move(bin_filename, abs_filename)
	
	if not os.listdir(bindir):
		print "%s files move complete" %bindir
	else:
		print os.listdir(bindir)
		print "somethin wrong!"
	
	
def DockerAutoMk():
	'''
	自动构建docker上线版本文件
	'''
	mkDir('tmp')
	RmSpcTree(DirName)
	NameField = FileNumCheck()
	MvFile(NameField[0])
	
	#根据基础构建还是增量构建选择不同模板，修改dockerfile和cfg_module.cfg
	flag = raw_input("deploy mode: base=1/increment=2  ")
	if flag == '1':
		#替换Dockerfile
		ReplaceStr('Dockerfile', *NameField)
		ReplaceStr('cfg_module.cfg', *NameField)
		mkDir(*FileList)
		shutil.copytree('stop-ats', NameField[0]+ os.sep +'stop-ats')
		shutil.move(NameField[0], 'dx'+ os.sep + NameField[0])
		shutil.move('cfg_module.cfg_tmp', 'dx'+ os.sep + 'cfg_module.cfg')
		shutil.copytree('mmp_init', 'dx'+ os.sep + 'mmp_init')
		
		
	elif flag == '2':
		#替换Dockerfile_extra
		ReplaceStr('Dockerfile_extra', *NameField)
		mkDir(*FileList)
		shutil.move(NameField[0], 'dx'+ os.sep + NameField[0])
		 
		
	else:
		print "no valid input, go die"
		exit(1)
	
	for dirname in FileList:
		shutil.move(dirname, 'tmp'+ os.sep + dirname)
	os.rename('tmp', NameField[1])
	
	if flag == '1':
		shutil.move('Dockerfile_tmp', NameField[1]+ os.sep + 'Dockerfile') 
		CheckFile = os.path.join(NameField[1], 'dx')
		os.system('md5_dep.exe '+ CheckFile)
	elif flag == '2':
		shutil.move('Dockerfile_extra_tmp', NameField[1]+ os.sep + 'Dockerfile')
		CheckFile = os.path.join(NameField[1], 'dx')
		os.system('md5_dep.exe '+ CheckFile) 
	else:
		print "no valid input, go die"
		exit(1)
	
	
def CommonAutoMk():
	'''
	自动构建老部署平台上线版本文件
	'''
	mkDir('tmp')
	NameField = FileNumCheck()
	print NameField
	BuildCity = raw_input("build city, for example dx: ")
	print BuildCity 

	BuildCity = BuildCity.split()
	print BuildCity

	if  len(BuildCity) != 0:
		first_city = BuildCity[0]
		os.rename(NameField[0], first_city)
		if len(BuildCity[1:]) != 0:
			for cityname in BuildCity[1:]:
				shutil.copytree(first_city, cityname)
	else:
		print "no valid input, go die"
		exit(1)
	
	TmpList = FileListExtra[:]
	[ TmpList.remove(element) for element in BuildCity ]
	mkDir(*TmpList)
	
	os.rename('tmp', NameField[1])
	for dirname in FileListExtra:
		NewFileName = os.path.join(NameField[1], dirname)
		print dirname, NewFileName
		shutil.move(dirname, NewFileName)
		if os.listdir(NewFileName):
			os.system('md5_dep.exe '+ NewFileName)
		
	
	
if __name__ == "__main__":
	print '''
1:	DockerAutoMk
2:	CommonAutoMk
3:	CreateDir
	'''
	select = raw_input("pls select make mode num: ")
	if select == '1':
		DockerAutoMk()
	elif select == '2':
		CommonAutoMk()
	elif select == '3':
		mkDir('tmp')
		mkDir(*FileList)
		for dirname in FileList:
			NewFileName = os.path.join('tmp', dirname)
			shutil.move(dirname, NewFileName)
	else:
		print "no valid input, go die"
		exit(1)