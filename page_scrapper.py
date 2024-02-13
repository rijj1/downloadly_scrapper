import requests
import bs4
import re
import os

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
REQUEST_HEADER={
    'User-Agent': USER_AGENT,
    'Accept-Language': 'en-US, en;q=0.5',
}

# Getting the html page
def get_page_html(url):
    res=requests.get(url=url, headers=REQUEST_HEADER)
    return res.content

def get_page_title(soup,page_info):
    title=''
    try:
        main_page_title=soup.find('h2',attrs={
            'class':"w-post-elm post_title us_custom_9de87d4e align_left entry-title color_link_inherit"
        })
        sample_title=main_page_title.find('a')
        title=sample_title.text.strip()
    except Exception as e:
        page_info['status_code'] = 400
        print(f"Error scraping Page Title: {e}")
    return title

def get_download_links(soup,url,page_info):
    download_links = {}
    try:
        download_sections = soup.find_all('h3', string=re.compile(r'download link', re.IGNORECASE))
        for download_section in download_sections:
            for link in download_section.find_next_siblings('p'):
                for child in link.findChildren('a'):
                    download_links[child.text]=child['href']
    
    except Exception as e:
        page_info['status_code'] = 400
        print(f"Error scraping Download Links: {e}")
    return download_links

def get_image(soup,page_info):
    image_link=''
    try:
        image_section = soup.find('div', class_='w-post-elm post_image us_custom_447bff20')
        image_link = image_section.find('img')['src']
    except Exception as e:
        page_info['status_code'] = 400
        print(f"Error scraping Image: {e}")
    return image_link

def save_image(url, page_info, image_dir='images'):
    image_filename=''
    try:
        image_filename = os.path.join(image_dir, os.path.basename(url))
        with open(image_filename, 'wb') as f:
            f.write(requests.get(url).content)
        print(f'Image saved to {image_filename}')
    except Exception as e:
        page_info['status_code'] = 400
        print(f"Error Saving Image: {e}")
    return image_filename
    
def page_info(url):
    page_info={}
    page_info['status_code'] = 200
    print(f'Scrapping URL: {url}')
    html= get_page_html(url=url)
    soup=bs4.BeautifulSoup(html,'lxml')
    page_info['scrap_url']=url
    page_info['title']=get_page_title(soup,page_info)
    page_info['download_links'] = get_download_links(soup,url,page_info)
    page_info['image_link']=get_image(soup,page_info)
    page_info['image']=save_image(page_info['image_link'],page_info)
    return page_info
