import requests

url = 'http://localhost:5000/gwas'
r = requests.post(url,json={'geno':"Barley WGS", 'pheno':"BGT_96hai"})

print(r.json())