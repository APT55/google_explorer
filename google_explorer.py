"""
Usage:
    google_explorer.py --dork=<arg> --browser=<arg> [--language=<arg>]
                                                    [--location=<arg>]
                                                    [--last_update=<arg>]
                                                    [--google_domain=<arg>]
                                                    [--proxy=<arg>]
    google_explorer.py --plugin=<arg>
    google_explorer.py --help
    google_explorer.py --version

Options:
    -h --help                                Open help menu
    -v --version                             Show version

Required options:
    --dork='google dork'                     your favorite g00gle dork :)
    --browser='browser'                      chrome
                                             chromium
    --plugin='plugins filters list'          joomla_cve_2015_8562
                                             wordpress_cve_2015_1579
                                             joomla_cve_2016_8870
                                             apache_rce_struts2_cve_2017_5638
                                             jboss_finder
                                             cors_misc
                                             verbose_sqli
                                             trace_axd
                                             drupalgeddonrce2
                                             joomla_joomanage

Optional options:
    --language='page language'               Portuguese
                                             English
                                             Arabic
                                             Romanian
                                             ...
                                             ...

    --location='server location'             Brazil
                                             Mauritania
                                             Tunisia
                                             Marroco
                                             Japan
                                             ...
                                             ...

    --last_update='page last update'         anytime
                                             past 24 hours
                                             past week
                                             past month
                                             past year

    --google_domain='google domain'          google domain to use on search.
                                             Ex: google.co.uk

    --proxy='ip:port'                        proxy ip:port

"""

import os
import os.path
import sys
import time

from plugins.pl_filter import Plugins

from docopt import docopt, DocoptExit
from lxml import html as lh

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait


filter_names = ['language', 'location', 'last_update',
                'google_domain', 'proxy']


class GoogleScanner:

    @staticmethod
    def banner():
        with open('utils/banner.txt') as f:
            os.system('clear')
            for line in f.readlines():
                print(line.rstrip())
            print('\n')

    def __init__(self, dork, browser, filters):
        self.dork = dork
        self.browser = browser
        self.filters = filters
        self.driver = self.validate_browser()

    def validate_browser(self):
        browser = self.browser
        f = self.filters
        driver = ''

        browsers_names = ['firefox', 'chrome', 'chromium']
        browsers_paths = {}
        binarys_path = '/usr/bin/'

        for file in os.listdir(binarys_path):
            for br in browsers_names:
                if br in file:
                    browsers_paths[br] = binarys_path + file

        if browser not in browsers_paths.keys():
            print('[###] No option for this browser [###]\n')
            print('Your current options are: \n')
            for b in browsers_paths.keys():
                print('- ' + b)
            print("\nIf you dont have any of them sorry for you =)..\n")
            sys.exit(1)

        if 'firefox' in browser:
            if f['proxy']:
                profile = webdriver.FirefoxProfile()
                profile.set_preference("network.proxy.type", 1)
                profile.set_preference("network.proxy.socks",
                                       f['proxy'].split(':')[0])
                profile.set_preference("network.proxy.socks_port",
                                       int(f['proxy'].split(':')[1]))
                profile.update_preferences()
                try:
                    driver = webdriver.Firefox(firefox_profile=profile)
                    driver.wait = WebDriverWait(driver, 90)
                    return driver
                except Exception as e:
                    print('[#] Error while executing geckodriver')
                    print('[#] Install geckodriver or upgrade it!')
                    print(str(e))
            else:
                try:
                    driver = webdriver.Firefox()
                    driver.wait = WebDriverWait(driver, 90)
                    return driver
                except Exception as e:
                    print('[#] Error while executing geckodriver')
                    print('[#] Install geckodriver or upgrade it!')
                    print(str(e))
        else:

            opts = Options()
            if f['proxy']:
                opts.add_argument('--proxy-server=socks5://%s' % f['proxy'])

            try:
                driver = webdriver.Chrome(browsers_paths[browser],chrome_options=opts)
                driver.wait = WebDriverWait(driver, 90)
                return driver
            except Exception as e:
                print('[#] Error with chromedriver')
                print('[#] Install chromedriver or upgrade/downgrade it!')
                print(str(e))

    def go_to_advanced_search_page(self):
        time.sleep(2)
        driver = self.driver
        options = {'first': {'tools_button': "//*[@id='ab_opt_icon']",
                             'advanced_search_option': "//*[@id='ab_as"
                             "and @href[contains(.,'/advanced_search')]]"},
                   'second': {'tools_button': "//*[@id='abar_button_opt']",
                              'advanced_search_option': "//div/"
                              "a[contains(@href,'advanced')]"}}
        for key, value in options.items():
            try:
                driver.find_element(By.XPATH, value['tools_button']).click()
                time.sleep(1)
                driver.find_element(By.XPATH,
                                    value['advanced_search_option']).click()
                break
            except Exception as e:
                pass

    def wait_for_presence(self, xpath):
        return self.driver.wait.until(EC.presence_of_element_located((
            By.XPATH, xpath)))

    def wait_for_clickable(self, xpath):
        self.wait_for_presence(xpath)
        return self.driver.wait.until(EC.element_to_be_clickable((
            By.XPATH, xpath)))

    def validate_and_select_option(self, option, options, option_button,
                                   argument_name):
        if option not in options:
            print("\n[###] No option for this argument... [###]\n")
            print("[*] The argument --" + argument_name +
                  " dont contains option: " + option)
            print("[*] Your current options are: \n")
            for op in options:
                print(op)
            self.driver.close()
            sys.exit(1)

        for _ in range(options.index(option) + 1):
            self.wait_for_presence(option_button).send_keys(Keys.ARROW_DOWN)

        self.wait_for_presence(option_button).send_keys(Keys.RETURN)

    def apply_filters(self):
        f = self.filters
        self.go_to_advanced_search_page()

        if f['language']:
            language_options_xpath = "//ul[@id='lr_menu']/li/div/text()"
            language_button = "//*[@id='lr_button']"
            arg = 'language'
            content = self.driver.page_source
            options = lh.fromstring(content)
            language_options = [op for op in options.xpath(
                language_options_xpath)]
            self.validate_and_select_option(f['language'], language_options,
                                            language_button, arg)

        if f['location']:
            location_options_xpath = "//ul[@id='cr_menu']/li/div/text()"
            location_button = "//*[@id='cr_button']"
            arg = 'location'
            content = self.driver.page_source
            options = lh.fromstring(content)
            location_options = [op for op in options.xpath(
                location_options_xpath)]
            self.validate_and_select_option(f['location'], location_options,
                                            location_button, arg)

        if f['last_update']:
            last_update_options_xpath = "//ul[@id='as_qdr_menu']/li/div/text()"
            last_update_button = "//*[@id='as_qdr_button']"
            arg = 'last_update'
            content = self.driver.page_source
            options = lh.fromstring(content)
            last_update_options = [op for op in options.xpath(
                last_update_options_xpath)]
            self.validate_and_select_option(f['last_update'],
                                            last_update_options,
                                            last_update_button, arg)

        # Making the search
        search_button = '//input[@type="submit"]'
        self.wait_for_clickable(search_button).click()

    def check_page_loaded(self):
        driver = self.driver
        navigation_bar_xpath = "//*[@id='foot']"
        try:
            driver.wait.until(EC.presence_of_element_located((
                By.XPATH, navigation_bar_xpath)))
            captcha = 'xxx'
            return captcha
        except Exception as e:
            captcha = None
            return captcha
            pass

    def write_results_to_file(self, results, filename):
        with open(filename, 'a') as f:
            for res in results:
                f.write(res + '\n')

    def result_parser(self):
        driver = self.driver

        print('[+] Starting parse search engine..')
        print('[+] Take a look at the screen to wait the captcha shows,'
              ' and type it')
        print('[+] The default time to wait you type the captcha is 20s')

        # Wait until captcha is checked
        check_page = self.check_page_loaded()
        while check_page is None:
            check_page = self.check_page_loaded()

        # Html parser and check if have a next page on pagination
        try:
            # Time splicit because of bug waiting to element using selenium time
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((
                By.ID, "pnnext")))
            next_page = driver.find_element_by_id("pnnext")
        except Exception as e:
            next_page = 'xxx'
            pass

        while next_page is not None:
            print('parsing links from page..')
            #links_xpath = ".//*[@id='rso']//h3/a[@onmousedown and @href or @href]/@href"
            links_xpath = "//*[@id='rso']//cite/text()"
            content = self.driver.page_source
            options = lh.fromstring(content)
            results = [link for link in options.xpath(links_xpath)]

            self.write_results_to_file(results, 'results_google_search.txt')

            try:
                driver.find_element_by_xpath("//*[@id='ofr']//a[@href]").click()
            except Exception as e:
                pass

            try:
                next_page = driver.find_element_by_id("pnnext")
                next_page.click()
                time.sleep(2)
                driver.wait.until(EC.presence_of_element_located((
                    By.XPATH, ".//*[@id='nav']")))
            except Exception as e:
                break

        driver.close()

    def check_google_domain(self, google_domain):
        from urllib.parse import urlparse
        google_url = 'http://www.google.com.br'
        google_domains_list = open('utils/google_domains.txt'
                                   ).read().splitlines()

        url_parsed = urlparse(google_domain)

        if 'www' in url_parsed.path or 'www' in url_parsed.netloc:
            print('\n[####] Please just put google domain in --google_domain'
                  'argument Ex: --google_domain="google.co.uk" [####]')
            print('Your option was: {0}'.format(google_domain))
            sys.exit(1)

        if url_parsed.path in google_domains_list:
            return 'http://www.' + url_parsed.path
        else:
            print('\n[+] Your current option was not find in google'
                  ' domains list: {0}'.format(google_domain))
            print('[+] Setting brazillian google as default =)))')
            return google_url

    def start_search(self):
        self.banner()

        driver = self.driver
        f = self.filters
        dork = self.dork

        # Checking google domain to search
        google_url = 'http://www.google.com.br'
        if f['google_domain']:
            google_url = self.check_google_domain(f['google_domain'])

        # Making the search
        driver.get(google_url)
        search_bar = driver.find_element_by_name("q")
        search_bar.send_keys(dork)
        search_bar.send_keys(Keys.RETURN)
        try:
            driver.wait.until(EC.presence_of_element_located((
                By.XPATH, "//*[@id='nav']")))
        except Exception as e:
            sys.exit(1)

        # Apply filters in arguments if necessary
        filters = dict((key, value) for key, value in f.items())
        if any(x is not None for x in filters.values()):
            self.apply_filters()

        # Preparing url to show more results
        driver.get(driver.current_url + '&num=100')
        time.sleep(1)

        self.result_parser()
        time.sleep(5)


def main():
    try:
        arguments = docopt(__doc__, version="anarc0der Google Explorer - 2016")
        dork = arguments['--dork']
        browser = arguments['--browser']
        pl_filters = arguments['--plugin']
        filters = {name: arguments['--%s' % name] for name in filter_names}

    except DocoptExit as e:
        GoogleScanner.banner()
        os.system('python google_explorer.py --help')
        sys.exit(1)

    if pl_filters:
        Plugins(pl_filters)
        sys.exit(0)

    if os.path.exists('results_google_search.txt'):
        if input('\n*** WARNING ***\n\nThere is old results stored in results file.\nIf you wanna keep them, press "Y": ') != "Y":
            os.remove('results_google_search.txt')

    myScan = GoogleScanner(dork, browser, filters)
    myScan.start_search()


if __name__ == '__main__':
    main()
