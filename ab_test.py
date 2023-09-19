import pandas as pd
import numpy as np
from scipy import stats
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import shapiro
import scipy.stats as stats


class AB_Test():

    """
    Класс для расчета статистик  и провдения АВ теста.
    На основе ноутбука
    https://www.kaggle.com/code/ekrembayar/a-b-testing-step-by-step-hypothesis-testing
    https://www.kaggle.com/code/babyoda/a-b-testing-in-practice"""
    print('Модуль AB_Test запустился')
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y

    def normality(self) -> bool:
        """
        Проверка на нормальность через тест Шапиро-Уилка (Shapiro-Wilk) на нормальность """
        # H0: Distribution is Normal! - False
        # H1: Distribution is not Normal! - True
        ntA = shapiro(self.x)[1] < 0.05
        ntB = shapiro(self.y)[1] < 0.05
        
        return ntA, ntB

    def test_type(self, ntA, ntB) -> float:

        if (ntA == False) & (ntB == False): # "H0: Normal Distribution"
            # Parametric Test
            # Assumption: Homogeneity of variances
            leveneTest = stats.levene(self.x, self.y)[1] < 0.05
            # H0: Homogeneity: False
            # H1: Heterogeneous: True

            if leveneTest == False:
                # Homogeneity
                ttest = stats.ttest_ind(self.x, self.y, equal_var=True)[1]
                # H0: M1 == M2 - False
                # H1: M1 != M2 - True
            else:
                # Heterogeneous
                ttest = stats.ttest_ind(self.x, self.y, equal_var=False)[1]
                # H0: M1 == M2 - False
                # H1: M1 != M2 - True
        else:
            # Non-Parametric Test
            ttest = stats.mannwhitneyu(self.x, self.y)[1] 
            # H0: M1 == M2 - False
            # H1: M1 != M2 - True

        return ttest

    def get_result(self) -> pd.DataFrame:
        """
        Получаем результат в виде датафрейма"""

        ntA, ntB = self.normality()
        ttest = self.test_type(ntA, ntB)

        result = pd.DataFrame({"AB Hypothesis":[ttest < 0.05], 
            "p-value":[ttest]})

        result["Test Type"] = np.where((ntA == False) & (ntB == False), "Parametric", "Non-Parametric")
        result["AB Hypothesis"] = np.where(result["AB Hypothesis"] == False, "Fail to Reject H0", "Reject H0")
        result["Comment"] = np.where(result["AB Hypothesis"] == "Fail to Reject H0", "A/B groups are similar!", "A/B groups are not similar!")

        # Columns
        if (ntA == False) & (ntB == False):
            result["Homogeneity"] = np.where(leveneTest== False, "Yes", "No")
            
            result = result[["Test Type", "Homogeneity","AB Hypothesis", "p-value", "Comment"]]
        else:
            result = result[["Test Type","AB Hypothesis", "p-value", "Comment"]]

        return result

    def get_image(self, title=None):
        plt.figure(figsize=(10, 8))
        # отрисовка графика распредения для первой выборки
        sns.histplot(self.x)
        # отрисовка графика распредения для второй выборки
        sns.histplot(self.y, fill=False, color="red")
        plt.axvline(self.x.mean(), ls='--', label = 'mean for the1st sp')               
        plt.axvline(self.y.mean(), color='red', ls='--', label = 'mean for the2st sp')
        plt.legend()
        if title != None:
            plt.title(title)
        plt.show()


class Hogwarts():
    """ Класс для разбиения датасета на две подвыборки для тетсирования гипотез"""
    print('Модуль Hogwarts запустился')
    def __init__(self, data, name, time_period):
        self.data = data
        self.name = name
        self.time_period = time_period

    def get_two_population(self):
        """получаем две подвыборки для анализа""" 
        data1 = self.data[(self.data.index > self.time_period[0])&(self.data.index <= self.time_period[1])]
        data2 = self.data[(self.data.index > self.time_period[2])&(self.data.index <= self.time_period[3])]
        data1 = pd.DataFrame(data1[self.name])
        data2 = pd.DataFrame(data2[self.name])
        data1 = data1.dropna()
        data2 = data2.dropna()
        x = np.array(data1, dtype=np.float32)
        y = np.array(data2, dtype=np.float32)

        x = np.reshape(x,-1)
        y = np.reshape(y,-1)

        return x, y
    
    def calc_defects(self, threshold1, threshold2=None):
        """
        Сравниваем данные с пороговым значение и формируем данные по принциу -брак- , -не брак-.
        threshold1 - float, может использоваться по умоланию для обоих подбыборок;
        threshold2 - float, можно добавить для второй выборки (может быть в разные периоды разные требования к значению)
        """
        
        x, y = self.get_two_population()
        if threshold2 == None:
            x = np.where(x < threshold1, 0, 1)
            y = np.where(y < threshold1, 0, 1)
        else:
            x = np.where(x < threshold1, 0, 1)
            y = np.where(y < threshold2, 0, 1)

        return x, y



if __name__ == '__main__':

    data = pd.read_csv(r'C:\Users\User\2_GIT\clickhouse-load\ab_test.csv',
                  index_col = 'DateTime', parse_dates=['DateTime'])

    name = 'UDISP_211_187945'  #  'UDISP_211_187945' 'UDISP_211_199186'
 
    start1 = pd.Timestamp('2022-02-01 00:00:00+0300')
    finish1 = pd.Timestamp('2022-03-01 00:00:00+0300')
    start2 = pd.Timestamp('2023-02-01 00:00:00+0300')
    finish2 = pd.Timestamp('2023-04-01 00:00:00+0300')
    time_period = [start1, finish1, start2, finish2]

    x, y = Hogwarts(data, name, time_period).get_two_population()
    result = AB_Test(x, y).get_result()
    print(' --- --- --- --- ')
    print(' ---  RESULT --- ')
    print(result)
    print(' --- --- --- --- ')
    
    AB_Test(x, y).get_image()

    print(' --- --- --- --- ')
    x, y = Hogwarts(data, name, time_period).calc_defects(360)
    result2 = AB_Test(x, y).get_result()
    print(' --- --- --- --- ')
    print(' ---  RESULT --- ')
    print(result2)
    print(' --- --- --- --- ')
