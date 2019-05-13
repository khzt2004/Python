# https://github.com/Speedml/notebooks/blob/master/titanic/titanic-solution-using-speedml.ipynb

from speedml import Speedml
import pandas as pd

df = pd.read_csv(
  "https://gist.githubusercontent.com/rgbkrk/a7984a8788a73e2afb8fd4b89c8ec6de/raw/db8d1db9f878ed448c3cac3eb3c9c0dc5e80891e/2015.csv"
)

sml = Speedml('https://gist.githubusercontent.com/rgbkrk/a7984a8788a73e2afb8fd4b89c8ec6de/raw/db8d1db9f878ed448c3cac3eb3c9c0dc5e80891e/2015.csv',
              'https://gist.githubusercontent.com/rgbkrk/a7984a8788a73e2afb8fd4b89c8ec6de/raw/db8d1db9f878ed448c3cac3eb3c9c0dc5e80891e/2015.csv', 
              target = 'Happiness Rank',
              uid = 'Country')
sml.shape()
sml.info()
sml.plot.importance()
data_exploratory = sml.eda()


sml.train.head()

sml.plot.correlate()


sml.plot.distribute()

sml.plot.continuous('Health (Life Expectancy)')

sml.feature.density('Health (Life Expectancy)')
sml.train[['Health (Life Expectancy)', 'Health (Life Expectancy)_density']].head()