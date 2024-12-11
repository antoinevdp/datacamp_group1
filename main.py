import time, re, datetime, json

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from matplotlib import pyplot as plt
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from tqdm import tqdm


class SteamScrapping:

    def __init__(self):
        options = webdriver.FirefoxOptions()
        options.add_argument("--headless")
        self.driver = webdriver.Firefox(options=options)

        self.link_games = []
        self.results = {"results": {}}
        self.key_games = []

    def getTable(self, element):
        rows = element.find_elements(By.TAG_NAME, "tr")

        header = rows[0].find_elements(By.TAG_NAME, "th")
        header_text = [col.text for col in header]

        data_rows = rows[1:]  # Exclude the header row

        return rows, header, data_rows

    def getTopGamesInfo(self, index_entries):
        self.driver.get("https://steamdb.info/charts/")
        xpath_select = '//*[@id="dt-length-0"]'
        select_element = self.driver.find_element(By.XPATH, xpath_select)
        select = Select(select_element)
        #select 500 games
        select.select_by_visible_text(index_entries)

        xpath_table = '//*[@id="table-apps"]'
        table_element = self.driver.find_element(By.XPATH, xpath_table)

        rows, header, data_rows = self.getTable(table_element)
        for row in data_rows:
            self.link_games.append(row.find_elements(By.TAG_NAME, "td")[2].find_element(By.TAG_NAME,"a").get_attribute('href'))
            cells = row.find_elements(By.TAG_NAME, "td")
            cell_text = [cell.text for cell in cells]
            self.key_games.append(cell_text[2])

        size = len(self.link_games)
        self.results["results"].update({"size": size})
        self.results["results"].update({"date": str(datetime.datetime.now())})
        self.results["results"].update({"games": {}})
        for game in data_rows :
            cells = game.find_elements(By.TAG_NAME, "td")
            cell_text = [cell.text for cell in cells]
            self.results["results"]["games"].update({cell_text[2]:{}})


    def getGameInfo(self, link, key_index):

        self.driver.get(link)
        xpath_table = '//*[@id="main"]/div/div[1]/div/div[2]/div[1]/table'
        element_present = WebDriverWait(self.driver, 1).until(
            EC.presence_of_element_located((By.XPATH, xpath_table))
        )
        table_element = self.driver.find_element(By.XPATH, xpath_table)
        rows, header, data_rows = self.getTable(table_element)

        for row in data_rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            cell_text = [cell.text for cell in cells]
            self.results["results"]["games"][self.key_games[key_index]].update({cell_text[0]:cell_text[1]})

    def getRatingGame(self, key_index):

        try :
            xpath = '/html/body/div[4]/div[1]/div/div[2]/div/div[2]/div[4]/ul[2]/li[2]/strong'
            element_present = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            rating_element = self.driver.find_element(By.XPATH, xpath)
            self.results["results"]["games"][self.key_games[key_index]].update({"rating":rating_element.text})
        except Exception as e:
            self.results["results"]["games"][self.key_games[key_index]].update({"rating": "N/A"})


    def getMonthlyPlayer(self, key_index):

        xpath = '//*[@id="chart-month-table"]'
        try :
            element_present = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            table_element = self.driver.find_element(By.XPATH, xpath)

            rows, header, data_rows = self.getTable(table_element)

            header_text = [col.text for col in header]
            self.results["results"]["games"][self.key_games[key_index]].update({"Monthly Player":{}})
            for i in range(3):
                self.results["results"]["games"][self.key_games[key_index]]["Monthly Player"].update(
                    {header_text[i]: []})
            for row in data_rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                cell_text = [cell.text for cell in cells]
                for i in range(3):
                    self.results["results"]["games"][self.key_games[key_index]]["Monthly Player"][header_text[i]].append(cell_text[i])



        except Exception as e:
            print("Can't get Monthly Player")
            self.results["results"]["games"][self.key_games[key_index]].update({"Monthly Player":None})

    def findTagElementException(self, xpath, key_index):
        element = self.driver.find_element(By.XPATH, xpath)
        tags = element.find_elements(By.TAG_NAME, "a")
        self.results["results"]["games"][self.key_games[key_index]].update({"Tags": []})
        for tag in tags:
            text = self.driver.execute_script("return arguments[0].textContent;", tag)
            self.results["results"]["games"][self.key_games[key_index]]["Tags"].append(text)


    def getTagGame(self, key_index):

        try :
            xpath = "/html/body/div[4]/div[1]/div/div[2]/div/div[2]/div[1]/div[7]/div[1]"
            element_present = WebDriverWait(self.driver, 1).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            self.findTagElementException(xpath, key_index)
        except Exception as e:
            try:
                xpath = "/html/body/div[4]/div[1]/div/div[2]/div/div[2]/div[1]/div[2]/div[1]"
                element_present = WebDriverWait(self.driver, 1).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                self.findTagElementException(xpath, key_index)
            except Exception as e:
                try:
                    xpath = "/html/body/div[4]/div[1]/div/div[2]/div/div[2]/div[1]/div[8]/div[1]"
                    element_present = WebDriverWait(self.driver, 1).until(
                        EC.presence_of_element_located((By.XPATH, xpath))
                    )
                    self.findTagElementException(xpath, key_index)
                except Exception as e:
                    self.results["results"]["games"][self.key_games[key_index]].update({"Tags": []})

    def getCurrentPrice(self, key_index):
        try :
            xpath = "/html/body/div[4]/div[1]/div/div[2]/div/div[2]/div[1]/div[4]/div[1]/table/tbody/tr[1]/td[2]"
            element = self.driver.find_element(By.XPATH, xpath)
            text = self.driver.execute_script("return arguments[0].textContent;", element)
            price = text
        except Exception as e:
            try :
                xpath = "/html/body/div[4]/div[1]/div/div[2]/div/div[2]/div[1]/div[5]/div[1]/table/tbody/tr[1]/td[2]"
                element = self.driver.find_element(By.XPATH, xpath)
                text = self.driver.execute_script("return arguments[0].textContent;", element)
                price = text
            except Exception as e:
                print("Can't get current price")
                price = "N/A"
        self.results["results"]["games"][self.key_games[key_index]].update({"Current Price":price})


    def __del__(self):
        self.driver.quit()

if __name__ == '__main__':
    scraper = SteamScrapping()
    scraper.getTopGamesInfo("25")

    for i, link in tqdm(enumerate(scraper.link_games)):
        print(link)
        scraper.getGameInfo(link, i)
        scraper.getRatingGame(i)
        scraper.getMonthlyPlayer(i)
        scraper.getTagGame(i)
        scraper.getCurrentPrice(i)

    with open('results.json', 'w') as outfile:
        outfile.write(json.dumps(scraper.results, indent=4))

