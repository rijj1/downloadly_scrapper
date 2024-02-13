import requests
import bs4
import page_scrapper as ps
from urllib.parse import quote
import csv
import html

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
REQUEST_HEADER = {
    'User-Agent': USER_AGENT,
    'Accept-Language': 'en-US, en;q=0.5',
}

token = 'BOT_TOKEN'
chat_id = 'CHAT ID'
max_retries = 3  # Set the maximum number of retries

def get_all_links(soup):
    links = soup.find_all('url')
    for link in links:
        for location in link.find('loc'):
            url=location.text.strip()
            retries=0
            while(retries < max_retries):
                content=ps.page_info(url)
                status=content['status_code']
                if status==200:
                    resp= upload_to_telegram(content)
                    if resp.status_code == 200:
                        break
                    else:
                        retries+=1
                        ret=str(retries)
                        response="Retrying (" + ret + ")"
                        print(response)
                else:
                    retries+=1
                    ret=str(retries)
                    response="Retrying (" + ret + ")"
                    print(response)
            else:
                failed_url=url
                with open('failed_uploads.txt', 'a') as file:
                    file.write(failed_url + '\n')
                print(f"Failed to upload to Telegram. Request URL added to 'failed_uploads.txt'")
                

def xml_link_extract(url):
    print(f'Scrapping URL in : {url}')
    html= ps.get_page_html(url=url)
    soup = bs4.BeautifulSoup(html, 'lxml-xml')
    get_all_links(soup)

def upload_to_telegram(text):
    title=text['title']
    title_mod = html.escape(title)
    title_mod = quote(title_mod, safe='')
    caption = '<b>' + title_mod + '</b>\n\n'
    caption += '<b>Download Links:</b>\n'
    for link_title, download_link in text['download_links'].items():
        caption += f'<a href="{download_link}">{link_title}</a>\n'
    file = {'photo': open(text['image'], 'rb')}
    txt = 'https://api.telegram.org/bot' + token + '/sendPhoto?chat_id=' + chat_id + '&caption=' + caption + '&parse_mode=HTML'
    resp = requests.post(txt, files=file)
    print(resp)
    return resp
    

if __name__=='__main__':
    with open('sitemap.csv', newline='') as csvfile:
        reader = csv.reader(csvfile,delimiter=',')
        for row in reader:
            url =row[0]
            xml_link_extract(url=url)
            result = 'Done with url: '+ url
            print(result)
