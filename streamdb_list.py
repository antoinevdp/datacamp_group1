from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

class SteamScrapping:

    def __init__(self):
        options = webdriver.FirefoxOptions()
        options.add_argument("--headless")
        self.driver = webdriver.Firefox(options=options)

    def getTopGamesInfo(self, index_entries):
        self.driver.get("https://steamdb.info/charts/")
        xpath_select = '//*[@id="dt-length-0"]'
        select_element = self.driver.find_element(By.XPATH, xpath_select)
        select = Select(select_element)
        #select 500 games
        select.select_by_index(index_entries)

        xpath_table = '//*[@id="table-apps"]'
        table_element = self.driver.find_element(By.XPATH, xpath_table)

        rows = table_element.find_elements(By.TAG_NAME, "tr")

        header = rows[0].find_elements(By.TAG_NAME, "th")
        header_text = [col.text for col in header]

        print(header_text)

        data_rows = rows[1:]  # Exclude the header row
        for row in data_rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            cell_text = [cell.text for cell in cells]
            print(cell_text)

        return data_rows[0].find_elements(By.TAG_NAME, "td")[2].find_element(By.TAG_NAME,"a").get_attribute('href')

    def getGameInfo(self, link):

        self.driver.get(link)
        xpath_table = '//*[@id="main"]/div/div[1]/div/div[2]/div[1]/table'
        table_element = self.driver.find_element(By.XPATH, xpath_table)
        print(table_element.text)

    def __del__(self):
        self.driver.quit()

if __name__ == '__main__':
    scraper = SteamScrapping()
    link = scraper.getTopGamesInfo(0)
    scraper.getGameInfo(link)