import rpy2.robjects.packages as rpackages
import rpy2.robjects as ro
from rpy2.robjects.lib import grdevices
from PIL import Image as image

# imports
ising_fit_r = rpackages.importr("IsingFit")
qgraph_r = rpackages.importr("qgraph")

# # Python portions (Missing headings)
# data = pd.read_csv("../file.csv")
# bopd = pd.read_csv("../bopd_cleaned_sav_file.csv")
# obama = pd.read_csv("../Obama.csv")

# X = data.values  # X is a matrix
# Y = bopd.values
# Z = obama.values

# automatic conversion of numpy objects into rpy2 objects
# numpy2ri.activate()

# n_rows, n_cols = X.shape
# X_r_format = ro.r.matrix(X)   # Calling R's matrix()
# ro.r.assign("X", X_r_format)  # equivalent to X <- as.matrix(X)

# to read in R style and shorten the wrapper file you can  do..
X = ro.DataFrame.from_csvfile("../file.csv")
Y = ro.DataFrame.from_csvfile("../bopd_cleaned_sav_file.csv")
Z = ro.DataFrame.from_csvfile("../Obama.csv")

Res = ising_fit_r.IsingFit(X)
Bop = ising_fit_r.IsingFit(Y)
Oba = ising_fit_r.IsingFit(Z)

# get the regular version with $q
with grdevices.render_to_bytesio(grdevices.jpeg, width=512, height=448, res=75) as img:
    qgraph_r.qgraph(Res.rx2("q"))

# Save file
with open("data.png", "wb") as png:
    png.write(img.getvalue())

# Image will open in a pop up
picture = image.open('data.png')
picture.show()


# get the slightly more precise version from the weighted adjacency matrices ($weiadj)
d = {Res: "Res.png", Bop: "Bop.png", Oba: "Oba.png"}
for i in d:
    print("We're in", d[i])
    with grdevices.render_to_bytesio(grdevices.jpeg, width=512, height=448, res=75) as img:
        qgraph_r.qgraph(i.rx2("weiadj"), layout="spring", cut=.8)

    print("Saving file")
    with open(d[i], "wb") as png:
        png.write(img.getvalue())

    print("Displaying file in pop up")
    picture = image.open(d[i])
    picture.show()
print("End of script. Warnings from R console will print if any:", "\n")
