#! /usr/bin/env python
#-*- coding: utf-8 -*-

__author__ = 'Andrew Li'
__date__ = '2015-10-20'
__version__info__ = (0,1,0)
__version__ = '.'.join(str(i) for i in __version__info__)

''' hack an apk file, and do some modifications '''

import os
import glob
import shutil
from config import *

outPath = 'out'

class ApkHacker(object):

    def __init__(self):
        path = APK_PATH
        if not os.path.exists(path):
            raise Exception('apk path not exist!')
        os.chdir(path)
        print 'go to %s' %(path)
        if os.path.exists(outPath):
            if os.path.isdir(outPath):
                print 'clean output dir...'
                shutil.rmtree(outPath)
        os.makedirs(outPath)        
        self.outPath = outPath
        print 'creating output dir...'
        
    def hack(self):
        fileList = glob.glob(r'.\*.apk')
        if len(fileList) == 0:
            print 'No apk file found!'
            exit()
        for file in fileList:
            print 'start process {}'.format(file)
            self.decodeApk(file)
            modify = self.modifyManifest(file)
            if modify:
                self.buildApk(file)
                self.signApk(file)
            self.cleanDir(file)
        print 'Complete all apk process!'    

    
    def decodeApk(self,file):
        os.system('apktool d ' + file)
    
    def modifyManifest(self,file):
        base,ext = os.path.splitext(file)
        manifest = os.path.join(base,'AndroidManifest.xml')
        inputFile = open(manifest, 'r')
        lines = inputFile.readlines()
        inputFile.close()
        bStartUsePermission = False
        bAdd = False
        try:
            outputFile = open(manifest, 'w')
            for line in lines:
                if (not bStartUsePermission) and -1 != line.find('uses-permission'):
                    bStartUsePermission = True
                if (not bAdd) and -1 != line.find('WRITE_EXTERNAL_STORAGE'):    
                    print 'already has permission WRITE_EXTERNAL_STORAGE'
                    return False
                if bStartUsePermission and (-1 == line.find('uses-permission')):
                    if not bAdd:
                        print 'no permission WRITE_EXTERNAL_STORAGE found, add permission'
                        outputFile.write(r'<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />' + '\n')
                        bAdd = True
                outputFile.write(line)
            outputFile.close()
            return True
        except:
            print 'open file {} error'.format(manifest)
            return False
    
    def buildApk(self, file):
        print 'build apk...'
        dirname, ext = os.path.splitext(file)
        filename = os.path.basename(file)
        if os.path.exists(dirname):
            if os.path.isdir(dirname):
                os.system('apktool b {} -o {}'.format(dirname, os.path.join(self.outPath,filename)))

    def signApk(self, file):
        print 'sign apk...'
        filename = os.path.basename(file)
        outname = os.path.join(self.outPath, filename)
        signCmd = 'jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore {} -storepass {} -keypass {} {} {}'.format(SIGN_KEYSTORE_PATH,SIGN_KEYSTORE_PASS,SIGN_KEY_PASS,outname,SIGN_ALIAS)
        print signCmd
        os.system(signCmd)

    def cleanDir(self, file):
        print 'clean dir...'
        dirname,ext = os.path.splitext(file)
        if os.path.exists(dirname):
            if os.path.isdir(dirname):
                shutil.rmtree(dirname)


if __name__ == '__main__':
    hack = ApkHacker()
    hack.hack()
