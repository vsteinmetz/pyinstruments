from hardware import vsa
import myPandas
import pandas
s = vsa.on_screen("A")
s2 = vsa.on_screen("B")

import myPandas.tools as t
df = vsa.on_screen()
df2 = vsa.on_screen()
df = t.add_top_label(df,"av0")
df2 = t.add_top_label(df2,"av1")
df_tot = pandas.concat([df,df2])


s = myPandas.Series([1,2,4,5,6,5,4,3,2,3,2])
s.fit("func_lorentz")