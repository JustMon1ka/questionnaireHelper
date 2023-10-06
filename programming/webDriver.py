import imp
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from random import randint
from random import sample
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import tools


class my_class(object):
    pass


class webRun:
    def __init__(self, url, times, apiKey, AiFlag) -> None:
        self.url = url
        self.times = times
        self.selections = []
        self.timeout = 0.3
        self.path = 0
        self.passtime = 0
        self.subpath = 0
        self.apiKey = apiKey
        self.AiFlag = AiFlag

    def run(self):

        for time in range(1, self.times + 1):
            driver = webdriver.Edge()
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
    Object.defineProperty(navigator, 'webdriver', {
      get: () => false
    })
  """
            })
            self.passtime = 0
            print(f"第{time}次填写问卷")
            driver.get(self.url)
            driver.implicitly_wait(10)
            for i in range(1, 100):

                if self.passtime >= 3:
                    break
                try:
                    print(f"第{i}题")
                    driver.implicitly_wait(self.timeout)
                    if i == 1 and time == 1:
                        for path in range(1, 10):
                            try:
                                element = driver.find_element(By.XPATH,
                                                              f"/html/body/div[1]/form/div[13]/div[{path}]/fieldset/div[{1}]/div[2]/div[1]/span/a")
                            except:
                                print("找不到元素")
                            else:
                                self.path = path
                                break
                    elementFlag = 1
                    try:  # 先找该题的题型，1=填空，3=选择，5=打分(是字符串类型的值)
                        ele = driver.find_element(By.XPATH,
                                                  f"/html/body/div[1]/form/div[13]/div[{self.path}]/fieldset/div[{i}]")
                        print(f"找到第{i}题对应的元素")
                    except:
                        print(f"未找到第{i}题对应的元素，将跳过")
                        self.selections.append(0)
                        self.passtime += 1
                        continue
                    else:
                        try:
                            elementFlag = ele.get_attribute("type")
                        except:
                            continue
                        if elementFlag is None:
                            print(f"第{i}题元素异常，将跳过")
                            self.selections.append(0)
                            continue
                        print(elementFlag)

                    className = ""
                    if elementFlag == '3':  # 选择题题型处理
                        element = driver.find_element(By.XPATH,
                                                      f"/html/body/div[1]/form/div[13]/div[{self.path}]/fieldset/div[{i}]/div[2]/div[1]/span/a")
                        className = str(element.get_attribute("class"))  # 如果是选择题，则根据class的值判断是单选还是多选
                        print(className)
                        if time == 1:  # 如果是选择题，则查询选项个数(仅第一遍进入，后续直接读取存入的信息）
                            selections = 0
                            for j in range(1, 10):
                                try:
                                    text = WebDriverWait(driver, self.timeout).until(
                                        EC.presence_of_element_located((By.XPATH,
                                                                        f"/html/body/div[1]/form/div[13]/div[{self.path}]/fieldset/div[{i}]/div[2]/div[{j}]/div[1]"))
                                    ).text
                                    print(text)
                                except TimeoutException:
                                    print(f"未在 {self.timeout} 秒内找到元素")
                                    break
                                else:
                                    if text.find("其他") == -1:
                                        selections += 1
                            self.selections.append(selections)
                            print(f"第{i}题：题型‘{className}’,选项个数：{selections}")
                        else:  # 如果是选择题，且不是第一遍填问卷，则直接读取第一遍存入的信息
                            selections = self.selections[i - 1]
                            print(f"第{i}题：题型‘{className}’,选项个数：{selections}")

                        if className == "jqradio":  # 单选
                            select = randint(1, selections)
                            print(select)
                            try:
                                driver.find_element(By.XPATH,
                                                    f"/html/body/div[1]/form/div[13]/div[{self.path}]/fieldset/div[{i}]/div[2]/div[{select}]/span/a").click()
                            except:
                                continue
                        elif className == "jqcheck":  # 多选
                            selectTimes = randint(1, selections)
                            integer_list = list(range(1, selections + 1))
                            samples = sample(integer_list, selectTimes)
                            print(samples)
                            for select in samples:
                                try:
                                    driver.find_element(By.XPATH,
                                                        f"/html/body/div[1]/form/div[13]/div[{self.path}]/fieldset/div[{i}]/div[2]/div[{select}]/span/a").click()
                                except:
                                    continue
                    elif elementFlag == '1':  # 填空题题型处理
                        if time == 1:
                            self.selections.append(0)
                        try:
                            driver.find_element(By.XPATH,
                                                f"/html/body/div[1]/form/div[13]/div[{self.path}]/fieldset/div[{i}]/div[2]/input").click()
                        except:
                            print(f"未找到第{i}题对应的元素，将跳过")
                            continue
                        if self.AiFlag:
                            question = driver.find_element(By.XPATH,
                                                           f"/html/body/div[1]/form/div[13]/div[{self.path}]/fieldset/div[{i}]/div[1]").text
                            print(f"第{i}题，题型：“填空题”,题目：{question} 将填入AI的回答：")
                            tool = tools.questionnaireTools(self.apiKey)
                            for _ in range(1, 3):
                                reply = "不知道"
                                try:
                                    reply = tool.getAIResponse(question)
                                except:
                                    continue
                                else:
                                    break
                        else:
                            print(f"第{i}题，题型：“填空题”,未启用Ai回复功能，统一填入”不知道“")
                            reply = "不知道"
                        # input("")
                        driver.find_element(By.XPATH,
                                            f"/html/body/div[1]/form/div[13]/div[{self.path}]/fieldset/div[{i}]/div[2]/input").send_keys(
                            reply)
                        continue
                    elif elementFlag == '5':  # 打分题题型处理
                        if time == 1:  # 第一遍时先检查该题有几个选项并储存
                            selections = 0
                            for j in range(1, 10):
                                try:
                                    text = WebDriverWait(driver, self.timeout).until(
                                        EC.presence_of_element_located((By.XPATH,
                                                                        f"/html/body/div[1]/form/div[13]/div[{self.path}]/fieldset/div[{i}]/div[2]/div/ul/li[{j}]/a"))
                                    ).text
                                    print(text)
                                except TimeoutException:
                                    print(f"未在 {self.timeout} 秒内找到元素")
                                    break
                                else:
                                    if text.find("其他") == -1:
                                        selections += 1
                            self.selections.append(selections)
                            print(f"第{i}题：题型‘打分题’,选项个数：{selections}")
                        else:
                            selections = self.selections[i - 1]
                            print(f"第{i}题：题型‘打分题’,选项个数：{selections}")

                        select = randint(1, selections)
                        print(select)
                        try:
                            driver.find_element(By.XPATH,
                                                f"/html/body/div[1]/form/div[13]/div[{self.path}]/fieldset/div[{i}]/div[2]/div/ul/li[{select}]/a").click()
                        except:
                            continue

                    # input("按任意键继续")
                except:
                    break

            #input("")
            if time == 1:
                for k in range(5, 15):
                    try:
                        driver.find_element(By.XPATH,
                                            f"/html/body/div[1]/form/div[13]/div[{k}]/div[3]/div/div/div").click()
                    except:
                        continue
                    else:
                        print(k)
                        self.subpath = k
                        break
            else:
                driver.find_element(By.XPATH,
                                    f"/html/body/div[1]/form/div[13]/div[{self.subpath}]/div[3]/div/div/div").click()

            sleep(1)
            driver.quit()

        # input("")
