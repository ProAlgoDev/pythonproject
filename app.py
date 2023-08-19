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
    def __init__(self, m_borough, m_block, m_lot, m_bbl):
        self.proc = True
        self.borough = m_borough
        self.block = m_block
        self.lot = m_lot
        self.bbl = m_bbl
        search_url = "https://a836-acris.nyc.gov/DS/DocumentSearch/BBL"
        op = webdriver.ChromeOptions()
        # custom_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        op.add_argument("--disable-blink-feature=AutomationControlled")
        # op.add_argument(f'--user-agent={custom_user_agent}')
        op.add_argument(f'--headless={True}')

        self.driver = webdriver.Chrome(options=op)
        self.driver.maximize_window()
        self.driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.driver.get(search_url)
        time.sleep(1)
    def search(self):
        
        if not os.path.exists(self.bbl):
            os.mkdir(self.bbl)
        borough_mapping = {'BK': '3', 'MN': '1',
                           'BX': '2', 'QN': '4', 'SI': '5'}
        try:
            dropelement = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//select[@name='borough']")))
            if dropelement:
                droplist = Select(dropelement)
                droplist.select_by_value(borough_mapping[self.borough])
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                (By.XPATH, "//*[@id='MT']/tbody/tr/td/form/table[1]/tbody/tr/td[2]/b/font/input"))).send_keys(self.block)
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                (By.XPATH, "//*[@id='MT']/tbody/tr/td/form/table[1]/tbody/tr/td[3]/b/font/input"))).send_keys(self.lot)
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                (By.XPATH, "//*[@id='MT']/tbody/tr/td/form/table[5]/tbody/tr[1]/td[1]/div/table/tbody/tr/td/input[1]"))).click()
            drop_max_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//select[@name='com_maxrows']")))
            if dropelement:
                drop_max_list = Select(drop_max_element)
                drop_max_list.select_by_value("99")
        except:
            pass

    def savecsv(self):

        csc = {}
        try:
            current = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                (By.XPATH, "/html/body/table[3]/tbody/tr[1]/td[2]/table/tbody/tr/td/font[2]"))).text
            patterns = {
                "Borough": r"Borough:\s+(.+)",
                "Block": r"Block:\s+(\d+)",
                "Lot": r"Lot:\s+(\d+)",
                "Date Range": r"Date Range:\s+(.+)",
                "Document Class": r"Document Class:\s+(.+)"
            }
            for field, pattern in patterns.items():
                match = re.search(pattern, current)
                if match:
                    csc[field] = match.group(1).strip()
            df = pd.DataFrame([csc])
            df = df.dropna(how="any")
            df.to_csv(f"{self.bbl}/Current Search Criteria.csv",
                      index=False, quoting=1)
            self.searchlist = []
            self.detlist = {}
            self.imagelist = {}
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
            dff = pd.DataFrame(self.searchlist)
            dff.to_csv(
                f"{self.bbl}/Search Results By Parcel Identifier.csv", index=None, header=False, quoting=1)
            self.fetchdata()
            
                
            self.driver.quit()
        except:
            self.driver.quit()
            pass

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
                    if num == 0 and flag == False and m_check == False:
                        tdlist.append(itm.text)
                    if num == 0:
                        try:
                            det = detaillist[numm].get_attribute("onClick")
                            det = det.split('"')[1]
                            try:
                                detid = ''
                                imgid = ''
                                detid = f"https://a836-acris.nyc.gov/DS/DocumentSearch/DocumentDetail?doc_id={det}"
                                imgid = f"https://a836-acris.nyc.gov/DS/DocumentSearch/DocumentImageView?doc_id={det}"
                                self.detlist[det] = detid
                                self.imagelist[det] = imgid
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
        
        num_iterations = len(self.imagelist)
     
        max_threads = 4

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
            # Submit tasks to the thread pool
            for task_number in range(num_iterations):
                executor.submit(self.fetchimg, task_number)
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
            # Submit tasks to the thread pool
            for task_number in range(num_iterations):
                executor.submit(self.fetchdet, task_number)

    def fetchdet(self,index):
        print("start")
        op = webdriver.ChromeOptions()
        # custom_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        op.add_argument("--disable-blink-feature=AutomationControlled")
        # op.add_argument(f'--user-agent={custom_user_agent}')
        op.add_argument(f'--headless={True}')

        driver = webdriver.Chrome(options=op)
        driver.maximize_window()
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        try:
            itemlist = list(self.detlist.items())
            key, value = itemlist[index]
            print(key)
            driver.get(value)
            detail = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                (By.XPATH, "/html/body/table[4]/tbody/tr/td/table[2]/tbody"))).text
            file = open(f"{self.bbl}/{key}.txt", "a")
            file.write(detail)
            file.close()
            driver.quit()
        except:
            driver.quit()

            pass

    def fetchimg(self,index):
        print("start")
        op = webdriver.ChromeOptions()
        # custom_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        op.add_argument("--disable-blink-feature=AutomationControlled")
        # op.add_argument(f'--user-agent={custom_user_agent}')
        op.add_argument(f'--headless={True}')
        download_folder = os.path.join(os.getcwd(), self.bbl)
        print(download_folder)
        op.add_experimental_option("prefs", {
            "download.default_directory": download_folder,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True
        })
        driver = webdriver.Chrome(options=op)
        driver.maximize_window()
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        try:
            itemlist = list(self.imagelist.items())
            key, value = itemlist[index]
            print(key)
            print(index)
            driver.get(value)
            iframe = WebDriverWait(driver, 20).until(EC.presence_of_element_located(
                (By.TAG_NAME, "iframe")))
            driver.switch_to.frame(iframe)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((
                By.XPATH, "//*[@id='vtm_main']/div[1]/table/tbody/tr/td[13]"))).click()
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                (By.XPATH, "//*[@id='vtm_main']/div[4]/div[2]/div/span[1]"))).click()
            check = True
            while check:
                for filename in os.listdir(download_folder):
                    if filename.lower().endswith(".pdf"):
                        if key in filename and filename.lower().endswith(".pdf"):
                            check = False
                            break
            driver.quit()
        except:
            print("error")
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
    dataList = []
    global cont
    if importCSV():
        for num, i in enumerate(dataList[cont:]):
            tmp = []
            initial(i,num)
            np.save("save.npy",num+1)
        statev.set("Done!")
    else:
        return


def initial(i,number):
    global cont
    instance = search(i["borough"], i["block"], i["lot"], i["bbl"])
    instance.search()
    global statev
    statev.set(i["bbl"])
    progressv.set(f"{number+1}/{len(dataList[cont:])}")
    instance.savecsv()

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
