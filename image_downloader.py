import re
import os
import shutil
import requests
import sys
import getopt
from bs4 import BeautifulSoup
import mysql.connector
from pathlib import Path

mydb = mysql.connector.connect(
host = "127.0.0.1",
user = "root",
password = "password",
database = "test",
port=3306,
auth_plugin='mysql_native_password'
)
newpath = Path.cwd() 
newpath = str(newpath) + "/storage/temp/"
if not os.path.exists(newpath):
    os.makedirs(newpath)
    
def img_name(key):
   URL = f'https://www.google.com/search?q={key}&tbm=isch'
     
   headinfo = {
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
      "Accept-Encoding": "gzip, deflate, br",
      "Accept-Language": "en-US,en;q=0.5",
      "Connection": 'keep-alive',
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0"
   }
   URL = f'https://www.google.com/search?q={key}&tbm=isch'
   page = requests.get(URL, headers=headinfo)
   soup = BeautifulSoup(page.content)
   script = soup.findAll('script')
   image_list = []
   for x in script:
      img = x.text
      a = re.findall(
         "(((https://www)|(http://)|(www))[-a-zA-Z0-9@:%_\+.~#?&//=]+)\.(jpg|jpeg|gif|png|bmp|tiff|tga|svg)", img)
      for i in a:
         full_url = i[0]+"."+i[5]
         image_list.append(full_url)
   count = 0
   while True:
      image_url = image_list[count]
      print("Image Url >> ",image_url)
      filename = image_url.split("/")[-1]
      full_filename = newpath + filename
      
      r = requests.get(image_url, stream=True)
      if r.status_code == 200:
         r.raw.decode_content = True
         with open(full_filename, 'wb') as f:
               shutil.copyfileobj(r.raw, f)
         print('Image sucessfully Downloaded: ', filename)
         break
      else:
         print('Image Couldn\'t be retreived')
      if count > 25:
         break
      count += 1
   return filename


def main(argv):
   tableid = ''
   keyword = ''

   try:
      opts, args = getopt.getopt(argv, "hi:k:", ["ifile=", "kfile="])
   except getopt.GetoptError:
      print('test.py -i <tableid> -k <keyword>')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print('test.py -i <tableid> -k <keyword>')
         sys.exit()
      elif opt in ("-i", "--ifile"):
         tableid = arg
      elif opt in ("-k", "--kfile"):
         keyword = img_name(arg)
         
   mycursor = mydb.cursor()
   sql = "UPDATE blog_asks SET thumbnail = '{0}'  WHERE id = '{1}' ".format(keyword,tableid)
   mycursor.execute(sql)
   mydb.commit()
   mydb.close()
   print('Table id >>> ', tableid)
   print('Img name >>> ', keyword)

if __name__ == "__main__":
   main(sys.argv[1:])
