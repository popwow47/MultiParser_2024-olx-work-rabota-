import flet as ft
import aiohttp
from bs4 import BeautifulSoup
import asyncio
import time
from fake_useragent import UserAgent
import re
from selenium.webdriver.common.keys import Keys
from  selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException



ua = UserAgent()

olx_headers = {"User-Agent":
"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
"Accept":
"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
"Accept-Encoding":
"gzip, deflate, br, zstd",
"Accept-Language":
"ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"
}

work_ua_headers = {"User - Agent":ua.random, #"Mozilla / 5.0(Windows NT 10.0;Win64;x64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 124.0.0.0Safari / 537.36",

    "Accept":
"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",

}


url_proxy = {"User-Agent":
"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
"Accept":"text / html, application / xhtml + xml, application / xml;q = 0.9, image / avif, image / webp, image / apng, * / *;q = 0.8, application / signed - exchange;v = b3;q = 0.7",
"Accept-Encoding":
"gzip, deflate, br, zstd",
"Accept-Language":
"ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"
}







work_url = f"https://www.work.ua/ru/jobs"



count  = 0

page_count = 1

def main(page: ft.Page):
    global page_count

    col_pages = ft.Text("Колличество страниц:  ")

    work_ua_query = ft.TextField(label="искомая вакансия",
                                 helper_text="ищем по всей стране(в будущих версиях возможно реализую по конкретным городам )",
                                 width=550,
                                 input_filter=ft.InputFilter(allow=True, replacement_string="",
                                                             regex_string=r"[0-9А-яA-Za-z,':.-\s/#+]+"),
                                 value="",disabled= True)

    def close_banner(e):
        page.banner.open = False
        page.update()

        # баннер ошибок

    def alert_banner(message):
        page.banner = ft.Banner(
            bgcolor=ft.colors.AMBER_100,
            leading=ft.Icon(ft.icons.WARNING_AMBER_ROUNDED, color=ft.colors.AMBER, size=40),
            content=ft.Text(message),
            actions=[ft.TextButton("Закрыть", on_click=close_banner), ])
        page.banner.open = True
        page.update()



    def rabota_selenium(e):
        space = " "
        sharp = "#"
        lv.controls.clear()
        if work_ua_query.value == "":
            rabota_url = f"https://robota.ua/ru/zapros/ukraine"

        else:

            if space in work_ua_query.value:
                work_ua_query.value = work_ua_query.value.replace(space,"-")
                if sharp in work_ua_query.value:
                    work_ua_query.value = work_ua_query.value.replace(sharp, "%2523")
            elif sharp in work_ua_query.value:
                    work_ua_query.value = work_ua_query.value.replace(sharp, "%2523")
            rabota_url = f"https://robota.ua/ru/zapros/{work_ua_query.value}/ukraine"

        options = webdriver.ChromeOptions()
        options.add_argument(f"user-agent= {ua.chrome}")

        options.add_argument("--disable-blink-features=AutomationControlled")  # отключениие режима webdriver
        options.add_argument("--headless")  # первый способ фонового режима Chrome driver
        driver = webdriver.Chrome(options=options)

        def scrol_page():
            for i in range(5):
                driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
                time.sleep(0.5)

        try:
            driver.get(url=rabota_url)
            time.sleep(0.1)

            scrol_page()

            def get_elements():
                global count
                try:
                    block = driver.find_element(By.XPATH,
                                                "/html/body/app-root/div/alliance-jobseeker-vacancies-root-page/div/alliance-jobseeker-desktop-vacancies-page/main/section/div")

                    title = block.find_elements(By.TAG_NAME, "h2")
                    link = block.find_elements(By.TAG_NAME, "a")
                    regex = "company"
                    pattern = re.compile(regex)

                    for element, l in zip(title, link):
                        count += 1

                        if pattern.search(l.get_attribute("href")) == None:
                            continue
                        else:

                            lv.controls.append(ft.Text(spans=[ft.TextSpan(str(count)), ft.TextSpan("           "),
                                                              ft.TextSpan(element.text), ft.TextSpan("                                                   "),
                                                              ft.TextSpan(l.get_attribute("href"),
                                                            ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE,color=ft.colors.BLUE),url=l.get_attribute("href"),),], ))

                            page.update()
                except NoSuchElementException as el:
                    alert_banner(el)
                    # print("при получении данных со страницы")
                    work_ua_query.value = ""
                time.sleep(0.5)


            pages = driver.find_element(By.XPATH, "/html/body/app-root/div/alliance-jobseeker-vacancies-root-page/div/alliance-jobseeker-desktop-vacancies-page/main/section/div/alliance-jobseeker-desktop-vacancies-list/div/div[41]/santa-pagination-with-links")#"/html/body/app-root/div/alliance-jobseeker-vacancies-root-page/div/alliance-jobseeker-desktop-vacancies-page/main/section/div/alliance-jobseeker-desktop-vacancies-list/div/div[41]")

            pgs = pages.find_elements(By.TAG_NAME, "a")


            for i in range(1, int(pgs[-2].text)+1):
                driver.get(url=f"{rabota_url}/?page={str(i)}")
                scrol_page()
                get_elements()


        except Exception as er:
            alert_banner(er)
            work_ua_query.value = ""
            page.update()
            #print(er)
        finally:
            driver.close()
            driver.quit()
            work_ua_query.value = None
            page.update()

    async def work_ua_get_page(session, pagec):

        global count
        global page_count

        if  work_ua_query.value == "":
            url = f"https://www.work.ua/ru/jobs/?ss={pagec}"
        else:

            url = work_url+f"/?page={pagec}"


        async with session.get(url=url, headers=work_ua_headers) as response:
            response_text = await response.text()

            soup = BeautifulSoup(response_text, "lxml")
            vacantions = soup.findAll("h2", class_="cut-top cut-bottom")

            for i in vacantions:


                purified = i.find('a').get('href').strip("/")

                title = (i.find("a").get("title"))

                link = (f'https://www.work.ua{purified.strip("ru")}')

                count+=1
                lv.controls.append(ft.Text(spans=[ft.TextSpan(str(count)),ft.TextSpan("           "),
                ft.TextSpan(title),ft.TextSpan("                                                   "),
                ft.TextSpan(
                    link,
                    ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE,color=ft.colors.BLUE),
                    url=link,

                ),

            ], ))

                time.sleep(0.01)
                page.update()

        work_ua_query.value = ""

        page_count+=1

        page.update()



    async def work_ua():
        lv.controls.clear()

        global work_url
        work_url = f"https://www.work.ua/ru/jobs-{work_ua_query.value}"

        rep = " "
        sharp = "#"
        if  work_ua_query.value == "":
            work_url = f"https://www.work.ua/ru/jobs/?ss="

        else:
            if rep in work_ua_query.value:
                work_ua_query.value = work_ua_query.value.replace(rep,"+")
                if sharp in work_ua_query.value:
                    work_ua_query.value = work_ua_query.value.replace(sharp, "%23")
            elif sharp in work_ua_query.value:
                    work_ua_query.value = work_ua_query.value.replace(sharp, "%23")


        async with aiohttp.ClientSession() as session:
            try:
                tasks = []

                response = await session.get(
                url=work_url,
                headers=work_ua_headers,

                )



                try:
                    soup = BeautifulSoup(await response.text(), "lxml")
                    pages = soup.findAll("a", class_="ga-pagination-default pointer-none-in-all")

                    if pages != None:
                        for q in range(int(pages[-1].text) + 1):
                            if q == 0:
                                continue
                            task = asyncio.create_task(work_ua_get_page(session, q))
                            tasks.append(task)
                        await asyncio.gather(*tasks)

                    else:
                        task = asyncio.create_task(work_ua_get_page(session, 1))
                        tasks.append(task)
                        await asyncio.gather(*tasks)



                except Exception as er:
                    page.snack_bar = ft.SnackBar(content=ft.Text("По данному запросу ничего не найдено"), open=False)
                    page.snack_bar.open = True
                    page.update()
                    alert_banner(er)
                    work_ua_query.value = ""
                    page.update()

            except Exception as ce:
                    alert_banner(ce)
                    work_ua_query.value = ""
                    page.update()



    def work_ua_main(e):
        global count
        global page_count
        count = 0
        page_count = 1
        col_pages.value = "Колличество страниц:  "
        col_pages.update()
        asyncio.run(work_ua())

    async def get_page_olx(session, pages):
        lv.controls.clear()
        global count
        global page_count
        olx_url = f"https://www.olx.ua/list/q-{work_ua_query.value}/?page={str(pages)}&search%5Border%5D=created_at%3Adesc" #f"https://www.olx.ua/list/q-{work_ua_query.value}/?search%5Border%5D=created_at:desc"

        async with session.get(url=olx_url, headers=olx_headers) as response:
            response_text = await response.text()



            soup = BeautifulSoup(response_text, "lxml")
            link = soup.findAll("a", class_="css-z3gu2d")

            for q in link:

                if q.find("h6") != None:
                    count += 1
                    # dt = []
                    title = q.find("h6")
                    link = "https://olx.ua" + q.get("href")

                    lv.controls.append(ft.Text(spans=[ft.TextSpan(str(count)), ft.TextSpan("           "),
                                                      ft.TextSpan(*title), ft.TextSpan(
                            "                        "),
                                                      ft.TextSpan(
                                                          link,
                                                          ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE,color=ft.colors.BLUE),
                                                          url=link,

                                                      ),],no_wrap=False ))
                    page.update()

        col_pages.value = f"Колличество страниц: {page_count} "
        page_count+=1
        page.update()

    async def olx_ua():

        olx_url = f"https://www.olx.ua/list/q-{work_ua_query.value}/?search%5Border%5D=created_at:desc"
        space = " "
        plus = "+"
        if work_ua_query.value == "":
            olx_url = f"https://www.olx.ua/list"

        else:
            if space in work_ua_query.value:
                work_ua_query.value = work_ua_query.value.replace(space, "-")
                if plus in work_ua_query.value:
                    work_ua_query.value = work_ua_query.value.replace(plus, "%2B")
            elif plus in work_ua_query.value:
                work_ua_query.value = work_ua_query.value.replace(plus, "%2B")

        async with aiohttp.ClientSession() as session:

            tasks = []
            try:
                response = await session.get(
                    url= olx_url
                    , headers=olx_headers)






                soup = BeautifulSoup(await response.text(), "lxml")
                pgs = soup.find("ul", class_="pagination-list css-1vdlgt7")

                if pgs == None:

                    task = asyncio.create_task(get_page_olx(session, 1))
                    tasks.append(task)
                    await asyncio.gather(*tasks)
                    work_ua_query.value = ""
                    page.update()


                else:

                    clrd = pgs.findAll("li")
                    for p in range(1,int(clrd[-1].text)+1):
                        task = asyncio.create_task(get_page_olx(session, p))
                        tasks.append(task)
                        await asyncio.gather(*tasks)
                    work_ua_query.value = ""
                    page.update()
            except Exception as ce:
                alert_banner(ce)




    def olx_ua_main(e):
        global count
        global page_count
        count = 0
        page_count = 1
        col_pages.value = "Колличество страниц:  "
        col_pages.update()
        asyncio.run(olx_ua())

    def checkboxes_changed(e):
        if chekbox_olx.value == True:
            chekbox_work.disabled = True
            chekbox_rabota.disabled = True
            parsse_btn.disabled = False
            work_ua_query.disabled = False
            parsse_btn.on_click = olx_ua_main
            work_ua_query.label = "искомый предмет"
            col_pages.value = "Колличество страниц:  "

            page.update()

        elif chekbox_work.value == True:
            chekbox_olx.disabled = True
            chekbox_rabota.disabled = True
            parsse_btn.on_click = work_ua_main
            parsse_btn.disabled = False
            work_ua_query.disabled = False
            col_pages.value = "Колличество страниц:  "
            page.update()

        elif chekbox_rabota.value == True:
            chekbox_work.disabled = True
            chekbox_olx.disabled = True
            parsse_btn.on_click = rabota_selenium
            parsse_btn.disabled = False
            work_ua_query.disabled = False
            col_pages.value = "Колличество страниц:  "
            page.update()

        else:
            chekbox_rabota.disabled = False
            chekbox_work.disabled = False
            chekbox_olx.disabled = False
            work_ua_query.disabled = True
            parsse_btn.disabled = True
            parsse_btn.on_click = None
            work_ua_query.label = "искомая вакансия"
            col_pages.value = "Колличество страниц:  "
            page.update()







    chekbox_olx = ft.Checkbox(label="olx.ua", value=False, on_change=checkboxes_changed,
                              adaptive=True)  # ,disabled= True)
    chekbox_work = ft.Checkbox(label="work.ua", value=False, on_change=checkboxes_changed,
                               adaptive=True)  # ,disabled= True)
    chekbox_rabota = ft.Checkbox(label="rabota.ua", value=False, on_change=checkboxes_changed,
                                 adaptive=True)  # ,disabled= True)


    parsse_btn = ft.ElevatedButton(text="спарсить", disabled= True)
    lv = ft.ListView(expand=1, spacing=10, padding=0, auto_scroll=True, divider_thickness=1)

    checkbox_panel = ft.Row([ft.Column([chekbox_olx, chekbox_work, chekbox_rabota]),work_ua_query])




    page.add(checkbox_panel,ft.Row([parsse_btn,col_pages]),lv)



if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    ft.app(main)