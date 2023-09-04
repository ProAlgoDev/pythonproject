from selenium import webdriver
from selenium.webdriver.support.ui import Select
import time
import os
import pandas as pd
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import threading
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import concurrent.futures
import numpy as np
class search():
    def __init__(self):
        
        search_url = "https://a836-acris.nyc.gov/DS/DocumentSearch/BBL"
        op = uc.ChromeOptions()
   
        op.add_argument("--disable-blink-feature=AutomationControlled")
        op.add_argument(f'--headless={True}')

        self.driver = uc.Chrome(options=op)
        self.driver.maximize_window()
        self.driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        time.sleep(1)
    
    def search(self, m_borough, m_block, m_lot, m_bbl):
        self.proc = True
        self.borough = m_borough
        self.block = m_block
        self.lot = m_lot
        self.bbl = m_bbl
        self.acris = ''
        self.zolaContent= ''
        self.bisweb = ''
        self.year = True
        search_url = "https://a836-acris.nyc.gov/DS/DocumentSearch/BBL"
        self.driver.get(search_url)
        borough_mapping = {'BK': '3', 'MN': '1',
                           'BX': '2', 'QN': '4', 'SI': '5'}
        try:
            dropelement = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//select[@name='borough']")))
            if dropelement:
                droplist = Select(dropelement)
                droplist.select_by_value(borough_mapping[self.borough])
            time.sleep(1)
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                (By.XPATH, "//*[@id='MT']/tbody/tr/td/form/table[1]/tbody/tr/td[2]/b/font/input"))).send_keys(self.block)
            time.sleep(.7)
            
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                (By.XPATH, "//*[@id='MT']/tbody/tr/td/form/table[1]/tbody/tr/td[3]/b/font/input"))).send_keys(self.lot)
            dropelement = WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.XPATH,"//select[@name='cmb_date']")))
            Select(dropelement).select_by_value("5Y")
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                (By.XPATH, "//*[@id='MT']/tbody/tr/td/form/table[5]/tbody/tr[1]/td[1]/div/table/tbody/tr/td/input[1]"))).click()
            try:
                noData = ''
                noData = WebDriverWait(self.driver,1).until(EC.presence_of_element_located((By.XPATH, "/html/body/form[1]/table/tbody/tr[2]/td/table/tbody/tr[2]/td/b"))).text
            except:
                pass
            if noData =='':
                drop_max_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//select[@name='com_maxrows']")))
                if dropelement:
                    drop_max_list = Select(drop_max_element)
                    drop_max_list.select_by_value("99")
                    self.year= True
                return True
            elif noData !='':
                self.acris  = noData+"\n"
                self.year = False
                return True
        except:
            pass
    def savecsv(self,end):

        try:
            self.searchlist = []
            self.detlist = {}
            self.imagelist = {}
            if self.year:
                self.resultsave(False, False)
                nav = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                    (By.XPATH, "/html/body/form[1]/table/tbody/tr[1]/td")))
                atcheck = True
                while atcheck:
                    try:
                        atag = WebDriverWait(nav, 5).until(
                            EC.presence_of_all_elements_located((By.TAG_NAME, "a")))
                        if len(atag) >= 1:
                            nexturl = ''
                            for i in atag:
                                if i.text == 'next':
                                    nexturl = i.get_attribute("href")
                                    print(nexturl)
                                    self.driver.get(nexturl)
                                    self.resultsave(True, True)
                            if nexturl == '':
                                break
                        if atcheck == False:
                            break
                    except:
                        print("Checknext")
                        atcheck = False
                        pass
                for i in self.searchlist:
                    for j in i:
                        temp = j.replace("\n"," ")
                        temp = temp + "\t\t"
                        self.acris +=temp
                    self.acris +="\n"
                self.acris +="--------------Details----------------\n"
                self.fetchdata()
            self.zola(self.bbl)
            content = ''
            content += self.zolaContent + "\n" + self.acris + "\n" + self.bisweb
            self.saveText(content)
            if end:
                self.driver.quit()
        except:
            pass
    def zola(self,bbl):
        print("f",bbl)
        temp = ''
        tmp = ''
        self.driver.get(f"https://zola.planning.nyc.gov/bbl/{bbl}")
        name=WebDriverWait(self.driver,20).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/header/header/div/div[1]/span"))).text
        det=WebDriverWait(self.driver,20).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div/div[3]/div/div[3]")))
        tax=WebDriverWait(self.driver,20).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div/div[3]/div/div[3]/label"))).text
        title=WebDriverWait(self.driver,20).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div/div[3]/div/div[3]/h1"))).text
        smallTitle=WebDriverWait(self.driver,20).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div/div[3]/div/div[3]/p"))).text
        lotSection=WebDriverWait(det,20).until(EC.presence_of_element_located((By.XPATH, ".//section[2]")))
        lot = lotSection.text
        neigh=WebDriverWait(det,20).until(EC.presence_of_element_located((By.XPATH, ".//section[3]"))).text
        temp += "NYC Planning ZoLa\n"
        temp +=name+"\n"
        temp+=tax+"\n"
        temp+=title+"\n"
        temp+=smallTitle+"\n"
        tmp = lot.splitlines()
        check = 0
        for index, i in enumerate(tmp):
            if check !=0 and index ==check:
                continue
            if "Building Info" in i:
                check = index+1
                continue
            if "Property Records" in i:
               check = index+1
               continue
            if "Housing Info" in i:
                check = index+1
                continue
            temp+=i+"\n"
        tmp = neigh.splitlines()
        check = 0
        for index, i in enumerate(tmp):
            if check !=0 and index ==check:
                continue
            if "Community District" in i:
                check = index+1
                continue
            if "City Council District" in i:
                check = index+1
                continue
            temp+=i+"\n"
        self.zolaContent =temp
        temp =''
        bisUrl = ''
        try:
            third = lotSection.find_elements(By.TAG_NAME, 'a')
            for j in third:
                if j.text == "BISWEB":
                    bisUrl = j.get_attribute("href")
                    print(bisUrl)
            self.driver.get(bisUrl)
        except:
            pass
        mainInfo = ''
        try:
            mainInfo = WebDriverWait(self.driver,20).until(EC.presence_of_element_located((By.XPATH, "//td[@class='maininfo']"))).text
            cellInfo = WebDriverWait(self.driver,20).until(EC.presence_of_element_located((By.XPATH, "/html/body/center/table[3]/tbody")))
        except:pass
        temp +="\n"+mainInfo+"\n"
        temp += self.tableData(cellInfo)

        # input("stop")
        self.bisweb =temp
    def saveText(self,content):
        file = open (f"{self.bbl}.txt","a")
        file.write(content)
        file.close()
    def resultsave(self, flag, m_flag):
        m_check = m_flag
        print("resultssave")
        try:
            table = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                (By.XPATH, "/html/body/form[1]/table/tbody/tr[2]/td/table/tbody")))
            tr = table.find_elements(By.XPATH, "tr")
            detaillist = WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((
                By.XPATH, "//input[@title='ViewDetail']")))
            for numm, i in enumerate(tr, start=0):
                if flag == True and numm == 0:
                    continue
                td = i.find_elements(By.XPATH, "td")
                tdlist = []
                for num, itm in enumerate(td, start=0):
                    # if num == 0 and flag == False and m_check == False:
                    #     tdlist.append(itm.text)
                    if num == 0:
                        try:
                            det = detaillist[numm].get_attribute("onClick")
                            det = det.split('"')[1]
                            try:
                                detid = ''
                                detid = f"https://a836-acris.nyc.gov/DS/DocumentSearch/DocumentDetail?doc_id={det}"
                                self.detlist[det] = detid
                            except:
                                pass
                        except:
                            print("next")
                            pass
                        continue
                    tdlist.append(itm.text)
                self.searchlist.append(tdlist)
        except:
            pass
   
    def fetchdata(self):
        num_iterations = len(self.detlist)
        max_threads = 4
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
            for task_number in range(num_iterations):
                executor.submit(self.fetchdet, task_number)
      
    def tableData(self,element):
        trData = element.find_elements(By.TAG_NAME, "tr")
        temp = ""
        for i in trData:
            tdData = i.find_elements(By.TAG_NAME, "td")
            for j in tdData:
                tmp = (j.text).replace("\n", " ")
                temp += tmp+"\t\t"
            temp += "\n"
        return temp
            

    def fetchdet(self,index):
        print("start")
        op = uc.ChromeOptions()
        op.add_argument("--disable-blink-feature=AutomationControlled")
        op.add_argument(f'--headless={True}')

        driver = uc.Chrome(options=op)
        driver.maximize_window()
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        try:
            itemlist = list(self.detlist.items())
            key, value = itemlist[index]
            print(key)
            driver.get(value)
            tempText = ''
            detailBody = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                (By.XPATH, "/html/body/table[4]/tbody/tr/td/table[2]/tbody/tr/td")))
            tempText =self.tableData(detailBody)
            try:
                th = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "/html/body/table[4]/tbody/tr/td/table[3]/tbody/tr[1]/td/table/tbody/tr[2]/td/table/tbody/tr")))
                thData = th.find_elements(By.TAG_NAME, "th")
                thText = ""
                for i in thData:
                    thText+=i.text + "\t\t"
                thText+="\n"
                party1 = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "/html/body/table[4]/tbody/tr/td/table[3]/tbody/tr[1]/td/table/tbody/tr[2]/td/div/table/tbody")))

                tempText+="PARTY1\n"
                tempText+=thText
                tempText += self.tableData(party1)
                tempText+="\n"

                party2 = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "/html/body/table[4]/tbody/tr/td/table[3]/tbody/tr[2]/td/table/tbody/tr[2]/td/div/table/tbody")))
                tempText+="PARTY2\n"
                tempText+=thText
                tempText += self.tableData(party2)
                tempText+="\n"

                party3 = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "/html/body/table[4]/tbody/tr/td/table[3]/tbody/tr[3]/td/table/tbody/tr[2]/td/div/table/tbody")))
                tempText+="PARTY3\n"
                tempText+=thText
                tempText += self.tableData(party3)
                tempText+="\n"

                parcel = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "/html/body/table[4]/tbody/tr/td/table[4]/tbody/tr/td/table[1]/tbody/tr[2]/td/div/table/tbody")))
                parcelTh = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "/html/body/table[4]/tbody/tr/td/table[4]/tbody/tr/td/table[1]/tbody/tr[2]/td/table/tbody/tr")))
                parcelThTag = parcelTh.find_elements(By.TAG_NAME, "th")
                tempText+="PARCELS\n"
                tmp = ''
                for i in parcelThTag:
                    tmp+=i.text
                    tmp+="\t\t"
                tempText+="\n"+tmp+"\n"
                tempText += self.tableData(parcel)
                tempText+="\n"
                refTh = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "/html/body/table[4]/tbody/tr/td/table[4]/tbody/tr/td/table[2]/tbody/tr[1]/td[1]/table/tbody/tr[2]/td/table/tbody/tr")))
                refThTag = refTh.find_elements(By.TAG_NAME, "th")
                tempText+="REFERENCES\n"
                tmp = ''
                for i in refThTag:
                    tmp+=i.text
                    tmp+="\t\t"
                tempText+="\n"+tmp+"\n"
                ref = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "/html/body/table[4]/tbody/tr/td/table[4]/tbody/tr/td/table[2]/tbody/tr[1]/td[1]/table/tbody/tr[2]/td/div/table/tbody")))
                tempText += self.tableData(ref)
                tempText+="\n"

                self.acris +=tempText
            except:
                print("refParty1")
                pass
            driver.quit()
        except:
            print("detailE")
            driver.quit()
            pass

def show_alert(msg):
    messagebox.showerror("Error", msg)

init_file_path = ''

def importCSV():
    global init_file_path
    global dataList
    global cont
    if init_file_path == '':
        show_alert("Select a csv file")
        statev.set("Error")
        return False
    csv = pd.read_csv(init_file_path, header=None, chunksize=1, skiprows=1)

    for row_num, chunk in enumerate(csv, start=0):
        tmp = {}
        tmp["borough"] = str(chunk.iloc[0, 0])
        tmp["block"] = str(chunk.iloc[0, 1])
        tmp["lot"] = str(chunk.iloc[0, 2])
        tmp["bbl"] = str(chunk.iloc[0, 3])

        dataList.append(tmp)
    if os.path.exists("save.npy"):
        num = ''
        cont = 0
        num = np.load("save.npy")
        if num !='':
            cont = num
    else:
        cont = 0
    return True

def open_file_dialog():
    global init_file_path
    init_file_path = filedialog.askopenfilename(
        filetypes=[("CSV file", "*.csv")])
    print("Selected file path:", init_file_path)
def start():
    thread = threading.Thread(target=starting)
    thread.daemon = True
    thread.start()
def starting():
    statev.set("Processing")
    global dataList
    global instance
    dataList = []
    instance = search()
    global cont
    
    if importCSV():
        for num, i in enumerate(dataList):
            tmp = []
            initial(i,num)
            # np.save("save.npy",num+1)
        statev.set("Done!")
    else:
        return


def initial(i,number):
    global cont
    global statev
    global instance
    textName = i["bbl"]+".txt"
    file = open(f"{textName}","w")
    file.write("")
    file.close()
    check = instance.search(i["borough"], i["block"], i["lot"], i["bbl"])
    statev.set(i["bbl"])
    progressv.set(f"{number+1}/{len(dataList)}")
    end = False
    if number == len(dataList):
        end = True
    if check:
        instance.savecsv(end)

font = ("Arial", 20)
root = tk.Tk()
root.title("App")
root.geometry("500x450")
open_button = tk.Button(root, text="Open CSV File",
                        width=20, height=2, command=open_file_dialog, font=font)
open_button.pack(padx=20, pady=50)
fetch_button = tk.Button(root, text="Start",
                         width=20, height=2, command=start, font=font)
fetch_button.pack(padx=20, pady=30)
statev = tk.StringVar()
statelabel = tk.Label(root, textvariable=statev, font=font)
statelabel.pack(padx=10, pady=10)
progressv = tk.StringVar()
font1 = ("Arial",18)

progress = tk.Label(root, textvariable=progressv, font=font1)
progress.pack(padx=10, pady=1)
root.mainloop()
