import imp
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from random import randint
from random import sample
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.edge.options import Options
import tools
import os


class my_class(object):
    pass


class webRun:
    def __init__(self, config, flags) -> None:
        self.url = config[0]
        self.times = int(config[1])
        self.apiKey = config[2]
        self.maxToken = config[3]
        self.AiFlag = flags.get("AiFlag").get()
        self.DebugFlag = flags.get("DebugFlag").get()
        self.PlusModeFlag = flags.get("PlusModeFlag").get()
        self.selections = []
        self.customization = {}  # 如果启用进阶模式，则使用该列表 其中的内容：{"(题号)":{"type":(single,multi),"choice":(a,b,c...),"expectations":(0-100)}}
        self.timeout = 0.3
        self.firstPath = 0
        self.secondPath = 0
        self.thirdPath = 0
        self.passtime = 0
        self.subpath = 0
        self.tool = tools.questionnaireTools(self.apiKey, self.maxToken)

    def run(self):
        options = Options()
        if self.DebugFlag:
            options.add_argument('--headless')  # 启用无头模式

        for time in range(1, self.times + 1):
            driver = webdriver.Edge(options=options)
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
                        for firstPath in range(1, 5):
                            try:
                                driver.find_element(By.XPATH,
                                                    f"/html/body/div[{firstPath}]/form")
                            except:
                                print("找不到元素")
                            else:
                                print(f"找到元素：firstPath={firstPath}")
                                self.firstPath = firstPath
                                break
                        for secondPath in range(12, 15):
                            flag = False
                            try:
                                driver.find_element(By.XPATH,
                                                    f"/html/body/div[{self.firstPath}]/form/div[{secondPath}]")
                            except:
                                print("找不到元素")
                            else:
                                print(f"找到元素：secondPath={secondPath}")
                                self.secondPath = secondPath
                            for thirdPath in range(1, 10):
                                try:
                                    driver.find_element(By.XPATH,
                                                        f"/html/body/div[{self.firstPath}]/form/div[{self.secondPath}]/div[{thirdPath}]/fieldset/div[1]")
                                except:
                                    print("找不到元素")
                                else:
                                    print(f"找到元素：thirdPath={thirdPath}")
                                    self.thirdPath = thirdPath
                                    flag = True
                                    break
                            if flag:
                                break
                    os.system('cls')
                    elementFlag = 1
                    try:  # 先找该题的题型，1=填空，2=大型填空，3=单项选择，4=多项选择，5=打分(1~5分打分题),8=打分题（0~100打分题）,12=总分100分的权重打分题(是字符串类型的值)
                        ele = driver.find_element(By.XPATH,
                                                  f"/html/body/div[{self.firstPath}]/form/div[{self.secondPath}]/div[{self.thirdPath}]/fieldset/div[{i}]")
                        print(f"第{i}题：{ele.text}")
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

                    if elementFlag == '3' or elementFlag == '4':  # 选择题题型处理
                        if time == 1:  # 如果是选择题，则查询选项个数(仅第一遍进入，后续直接读取存入的信息）
                            selections = 0
                            for j in range(1, 10):
                                try:
                                    text = WebDriverWait(driver, self.timeout).until(
                                        EC.presence_of_element_located((By.XPATH,
                                                                        f"/html/body/div[{self.firstPath}]/form/div[{self.secondPath}]/div[{self.thirdPath}]/fieldset/div[{i}]/div[2]/div[{j}]/div"))
                                    ).text
                                    #print(j,".",text)
                                except TimeoutException:
                                    print(f"未在 {self.timeout} 秒内找到新的选项")
                                    break
                                else:
                                    if text.find("其他") == -1:
                                        selections += 1
                            self.selections.append(selections)
                        else:  # 如果是选择题，且不是第一遍填问卷，则直接读取第一遍存入的信息
                            selections = self.selections[i - 1]

                        if elementFlag == '3':  # 单选
                            print(f"第{i}题，题型：单选，选项个数：{selections}")
                            if self.PlusModeFlag:
                                if time == 1:
                                    self.customization[str(i)] = {"type": "single"}
                                    choice = input(
                                        "请输入预期选项（输入数字：A=1，B=2...），输入0则此题不启用定制（保持完全随机）")
                                    self.customization[str(i)]["choice"] = choice
                                    if choice != "0":
                                        expectations = input("请输入你希望该选项出现的概率（0-100）")
                                        self.customization[str(i)]["expectations"] = expectations
                                else:
                                    data = self.customization.get(str(i))
                                    choice = data.get("choice")
                                    expectations = data.get("expectations")
                                    print(data)
                            else:
                                choice = "0"

                            if self.PlusModeFlag and choice != "0":
                                select = self.tool.getSelections(selections, choice, int(expectations))[0]
                            else:
                                select = randint(1, selections)

                            print(f"选择：{select}")

                            try:
                                driver.find_element(By.XPATH,
                                                    f"/html/body/div[{self.firstPath}]/form/div[{self.secondPath}]/div[{self.thirdPath}]/fieldset/div[{i}]/div[2]/div[{select}]/span/a").click()
                            except:
                                continue
                        elif elementFlag == '4':  # 多选
                            title = driver.find_element(By.XPATH,  # 首先找到该题题目，判断是否有最少选择和最大选择限制
                                                        f"/html/body/div[{self.firstPath}]/form/div[{self.secondPath}]/div[{self.thirdPath}]/fieldset/div[{i}")
                            minvalue = title.get_attribute("minvalue")
                            maxvalue = title.get_attribute("maxvalue")
                            minselection = int(minvalue) if minvalue is not None else 1
                            maxselection = int(maxvalue) if maxvalue is not None else selections
                            selectTimes = randint(minselection, maxselection)  # 根据题目要求在范围内随机抽取选择个数
                            print(
                                f"第{i}题，题型：多选，选项个数：{selections}，将随机选择{minselection}——{maxselection}项选项")
                            if self.PlusModeFlag:
                                if time == 1:
                                    self.customization[str(i)] = {"type": "single"}
                                    choice = input(
                                        "请输入预期选项（eg.1246（表示期望选项为ABDF，数字之间不加间隔符）），输入0则此题不启用定制（保持完全随机）")
                                    self.customization[str(i)]["choice"] = choice
                                    if choice != "0":
                                        expectations = input("请输入你希望该选项出现的概率（0-100）")
                                        self.customization[str(i)]["expectations"] = expectations
                                else:
                                    data = self.customization.get(str(i))
                                    choice = data.get("choice")
                                    expectations = data.get("expectations")
                                    print(data)
                            else:
                                choice = "0"
                            if self.PlusModeFlag and choice != "0":
                                selects = self.tool.getSelections(selections, choice, int(expectations))
                            else:
                                integer_list = list(range(1, selections + 1))
                                selects = sample(integer_list, selectTimes)
                            print(f"选择了：{selects}")
                            for select in selects:
                                try:
                                    driver.find_element(By.XPATH,
                                                        f"/html/body/div[{self.firstPath}]/form/div[{self.secondPath}]/div[{self.thirdPath}]/fieldset/div[{i}/div[2]/div[{select}]/span/a").click()
                                except:
                                    continue
                    elif elementFlag == '1' or elementFlag == '2':  # 填空题题型处理
                        if time == 1:
                            self.selections.append(0)
                        if elementFlag == '1':
                            try:
                                inputelement = driver.find_element(By.XPATH,
                                                                   f"/html/body/div[{self.firstPath}]/form/div[{self.secondPath}]/div[{self.thirdPath}]/fieldset/div[{i}/div[2]/input")
                                inputelement.click()
                            except:
                                print(f"未找到第{i}题对应的元素，将跳过")
                                continue
                        else:
                            try:
                                inputelement = driver.find_element(By.XPATH,
                                                                   f"/html/body/div[{self.firstPath}]/form/div[{self.secondPath}]/div[{self.thirdPath}]/fieldset/div[{i}/div[2]/textarea")
                                inputelement.click()
                            except:
                                print(f"未找到第{i}题对应的元素，将跳过")
                                continue
                        if self.AiFlag:
                            question = driver.find_element(By.XPATH,
                                                           f"/html/body/div[{self.firstPath}]/form/div[{self.secondPath}]/div[{self.thirdPath}]/fieldset/div[{i}/div[1]").text
                            print(f"第{i}题，题型：“填空题”,题目：{question} 将填入AI的回答：")
                            for _ in range(1, 3):
                                reply = "不知道"
                                try:
                                    reply = self.tool.getAIResponse(question)
                                except:
                                    continue
                                else:
                                    break
                        else:
                            print(f"第{i}题，题型：“填空题”,未启用Ai回复功能，统一填入”不知道“")
                            reply = "不知道"
                        # input("")
                        inputelement.send_keys(
                            reply)
                        continue
                    elif elementFlag == '5':  # 打分题题型处理

                        if time == 1:  # 第一遍时先检查该题有几个选项并储存
                            selections = 0
                            for j in range(1, 10):
                                try:
                                    text = WebDriverWait(driver, self.timeout).until(
                                        EC.presence_of_element_located((By.XPATH,
                                                                        f"/html/body/div[{self.firstPath}]/form/div[{self.secondPath}]/div[{self.thirdPath}]/fieldset/div[{i}/div[2]/div/ul/li[{j}]/a"))
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
                                                f"/html/body/div[{self.firstPath}]/form/div[{self.secondPath}]/div[{self.thirdPath}]/fieldset/div[{i}/div[2]/div/ul/li[{select}]/a"
                                                ).click()
                        except:
                            continue
                    elif elementFlag == "8":  # 0~100的打分题
                        if time == 1:
                            self.selections.append(0)
                        score = randint(1, 100)
                        print(score)
                        try:
                            driver.find_element(By.XPATH,
                                                f"/html/body/div[{self.firstPath}]/form/div[{self.secondPath}]/div[{self.thirdPath}]/fieldset/div[{i}/input").send_keys(
                                str(score))
                        except:
                            continue

                    # input("按任意键继续")
                except Exception as e:
                    print(e)
                    break

            #input("")
            if time == 1:
                for k in range(5, 15):
                    try:
                        driver.find_element(By.XPATH,
                                            f"/html/body/div[{self.firstPath}]/form/div[{self.secondPath}]/div[{k}]/div[3]/div/div/div").click()
                    except:
                        continue
                    else:
                        print(k)
                        self.subpath = k
                        break
            else:
                driver.find_element(By.XPATH,
                                    f"/html/body/div[{self.firstPath}]/form/div[{self.secondPath}]/div[{self.subpath}]/div[3]/div/div/div").click()

            sleep(1)
            driver.quit()

        # input("")
