from flask import Flask
import random
import pickle
from estnltk import Text
from estnltk.vabamorf.morf import synthesize

app = Flask(__name__)

# sõnastik, milles on võõrsõnad koos vihjetega
sõnastik = {}
with open('saveSonastik.pickle', 'rb') as handle:
    sõnastik = pickle.load(handle)
kerged = []# kergete võõrsõnade grupp
with open('saveKerged.pickle', 'rb') as handle:
    kerged = pickle.load(handle)
keskmised = []# keskmiste võõrsõnade grupp
with open('saveKeskm.pickle', 'rb') as handle:
    keskmised = pickle.load(handle)
# laen laused pickle-failist sisse
# testimiseks kasutan ainult kergeid ja keskmisi võõrsõnu
laused = {}
with open('saveLausedKergedKeskm.pickle', 'rb') as handle:
    laused = pickle.load(handle)

paarid = []# sarnaste võõrsõnade paarid, mis on vajalikud teise mängu jaoks
with open('savePaarid.pickle', 'rb') as handle:
    paarid = pickle.load(handle)

def leiaVorm(sona):
    return Text(sona).tag_layer().morph_analysis.form[0][0]

def leiaValdkond(valdkond):
    valdkonnad = {'aiand': 'aiandus', 'aj': 'ajalugu', 'anat': 'anatoomia', 'antr': 'antropoloogia',
                  'arheol': 'arheoloogia', 'arhit': 'arhitektuur','astr': 'astronoomia', 'bibl': 'bibliograafia',
                  'biol': 'bioloogia', 'bot': 'botaanika', 'dipl': 'diplomaatia', 'eh': 'ehitus', 'el': 'elektroonika',
                  'etn': 'etnoloogia', 'farm': 'farmaatsia', 'fil': 'filosoofia', 'film': 'filmindus', 'folkl': 'folkloor',
                  'fot': 'fotograafia', 'füsiol': 'füsioloogia', 'füüs': 'füüsika', 'geod': 'geodeesia', 'geogr': 'geograafia',
                  'geol': 'geoloogia', 'hüdrol': 'hüdroloogia', 'info': 'informaatika', 'jur': 'juriidika', 'keem': 'keemia',
                  'kirj': 'kirjandus', 'kok': 'kokandus', 'kunst': 'kunst', 'lenn': 'lennundus', 'lgv': 'lingvistika', 'loog': 'loogika',
                  'maj': 'majandus', 'mat': 'matemaatika', 'med': 'meditsiin', 'mer': 'merendus', 'meteor': 'meteoroloogia',
                  'mets': 'metsandus', 'miner': 'mineraloogia', 'muus': 'muusika', 'mäend': 'mäendus', 'müt': 'mütoloogia',
                  'paleont': 'paleonoloogia', 'ped': 'pedagoogika', 'pol': 'poliitika', 'psühh': 'psühholoogia', 'põll': 'põllumajandus',
                  'relig': 'religioon', 'sotsiol': 'sotsioloogia', 'sport': 'sport', 'stat': 'statistika', 'sõj': 'sõjandus', 'zool': 'zoologia',
                  'tants': 'tants', 'teater': 'teater', 'tehn': 'tehnika', 'tekst': 'tekstiil', 'trük': 'trükindus', 'vet': 'veterinaaria', 'ökol': 'ökoloogia'}
    return valdkonnad[valdkond]

# leiame sõnastikust õigele võõrsõnale vastavad laused ja valime nendest suvalise
def leiaLause(sõna):
    lauseOsad = laused[sõna][random.randint(0, len(laused[sõna]) - 1)]
    return (lauseOsad[0] + " __ " + lauseOsad[1], lauseOsad[-1])

def leiaVihjed(sõna):
    sonavormid = {'S': 'nimisõnaga', 'V': 'tegusõnaga', 'A': 'omadussõnaga', 'P': 'asesõnaga', 'N': 'põhiarvsõnaga', 
                  'I': 'hüüdsõnaga', 'J': 'sidesõnaga', 'G': 'omastavalise täiendiga', 'D': 'määrsõnaga'}
    # Lisan kõik vihjed eraldi nimekirja ja leian kui palju vihjeid on kokku
    nimekiri = []
    #vormid = []
    if sõnastik[sõna][0] != "" and sõnastik[sõna][3] != "":
        nimekiri.append("Selle sõna valdkond on "+ leiaValdkond(sõnastik[sõna][0])+". " + "Tegemist on "+ sonavormid[sõnastik[sõna][3]]+".\n")
        #if sõnastik[sõna][3] not in vormid:
        #    vormid.append(sõnastik[sõna][3])
    if type(sõnastik[sõna][1]) is list:
        tulemuse = "Selle võõrsõna definitsioonid on:\n"
        for t in sõnastik[sõna][1]:
            t = t.replace(" vm ", " või muu ")
            t = t.replace(" a-ni ", " aastani ")
            t = t.replace(" kasut ", " kasutatakse ")
            t = t.replace(" hrl ", " harilikult ")
            t = t.replace(" v ", " või ")
            tulemuse += " *" + t + "\n"
        nimekiri.append(tulemuse)
    elif type(sõnastik[sõna][1]) is str:
        sõnastik[sõna][1] = sõnastik[sõna][1].replace(" vm ", " või muu ")
        sõnastik[sõna][1] = sõnastik[sõna][1].replace(" a-ni ", " aastani ")
        sõnastik[sõna][1] = sõnastik[sõna][1].replace(" kasut ", " kasutatakse ")
        sõnastik[sõna][1] = sõnastik[sõna][1].replace(" hrl ", " harilikult ")
        sõnastik[sõna][1] = sõnastik[sõna][1].replace(" v ", " või ")
        nimekiri.append("Selle võõrsõna definitsioon on: "+sõnastik[sõna][1]+".\n")
    if sõnastik[sõna][2] != "":
        nimekiri.append("Selle sõna vastandsõna on "+ sõnastik[sõna][2]+".\n")
    nimekiri.append("See sõna algab "+sõna[0].upper()+" tähega.\n")
    nimekiri.append("Selle võõrsõna pikkus on "+ str(len(sõna))+ " tähte.\n")
    lause, oigesKaandes = leiaLause(sõna)
    nimekiri.append("Mul on sulle üks näidislause:\n" + lause + "\n")
    #print(vormid)
    return (oigesKaandes, nimekiri)

# Members API route
@app.route("/members")
def members(): 
    return {"members": ["Member1", "Member2", "Member3"]}

@app.route("/main")
def main():
    return

@app.route("/mang1")
def mang1():
    # Võtan sõnastikust välja 5 sõna ja nendega seotud vihjet testimiseks
    sonad = []
    v = []
    for i in range(5):
        sona = kerged[random.randint(0, len(kerged) - 1)]
        oigesKaandes, vihjed = leiaVihjed(sona)
        lisa = {"sõna": [sona, oigesKaandes], "raskus": "kerge", "vihjeteNkr": vihjed}
        '''{
            "valdkond": vihjed[0],
            "def": vihjed[1],
            "vastand": vihjed[2],
            "vorm": vihjed[3]
                 }'''
        sonad.append(lisa)
        v.append(vihjed)
        i+=1
    for i in range(5):
        sona = keskmised[random.randint(0, len(keskmised) - 1)]
        oigesKaandes, vihjed = leiaVihjed(sona)
        lisa = {"sõna": [sona, oigesKaandes], "raskus": "keskmine", "vihjeteNkr": vihjed}
        '''{
            "valdkond": vihjed[0],
            "def": vihjed[1],
            "vastand": vihjed[2],
            "vorm": vihjed[3]
                 }'''
        sonad.append(lisa)
        v.append(vihjed)
        i+=1
    return sonad

@app.route("/mang2")
def mang2():
    sonad = []
    for i in range(10):
        while True:
            paar = paarid[random.randint(0, len(kerged) - 1)]
            if ((paar[0] in kerged or paar[0] in keskmised) and (paar[1] in kerged or paar[1] in keskmised)):
                print("Leidsin!")
                break
        # asendus: paar[0], leitav: paar[1]
        lauseOsad = laused[paar[1]][random.randint(0, len(laused[paar[1]]) - 1)]
        lauseOsad[0] = lauseOsad[0].replace("<p>", "")
        lauseOsad[1] = lauseOsad[1].replace("</p>", "")
        vorm = leiaVorm(lauseOsad[-1])#igaks juhuks võtan viimase elemendi, sest mõne puhul on lauselõpupunkt eraldi
        asendus = synthesize(paar[0], vorm)[0]
        asenduseAsendus = ""
        if lauseOsad[-1][0].isupper():
            asenduseAsendus = asendus[0].upper() + asendus[1:]
        if asenduseAsendus == "":
            asenduseAsendus = asendus
        # lauseOsad[-1] -> mõnel sõnal võib olla mõttekriips lõpus või mõni muu üleliigne kirjavahemärk juures
        lisa = {"õige": [paar[1], lauseOsad[-1]], "vasak": lauseOsad[0], "parem": lauseOsad[1], "asendus": asenduseAsendus}
        print(lauseOsad)
        sonad.append(lisa)
        i += 1
    # Tagastan sõnastikuna, et saaks kuvada õige info kasutajale
    # õige: vastus, mille kasutaja peab sisestama [lemma, õiges vormis]
    # vasak: lause vasak pool
    # parem: lause parem pool
    # asendus: õiges vormis asendatud sõna, mis on vale (õige võõrsõna asemel)
    return sonad

# lisafunktsioon selleks, et leida kõik ühest valdkonnast pärit võõrsõnad
# vajalik kolmanda mängu jaoks
def leiaSamastValdkonnast(valdkond):
    kokku = []
    # hetkel jätan kõik raskete grupi sõnad välja
    yhendatud = kerged + keskmised
    for key in yhendatud:
        if sõnastik[key][0] == valdkond:
            kokku.append(key)
    return kokku

@app.route("/mang3")
def mang3():
    # Kolmanda mängu jaoks on vaja valida üks valdkond
    # Valin neli suvalist lauset ja kuus võõrsõna
    valdkonnad = ['aiand', 'aj', 'anat', 'antr', 'arheol', 'arhit', 'astr', 'bibl', 'biol', 'bot', 'dipl', 
                  'eh', 'el', 'etn', 'farm', 'fil', 'film', 'folkl', 'fot', 'füsiol', 'füüs', 'geod', 
                  'geogr', 'geol', 'hüdrol', 'info', 'jur', 'keem', 'kirj', 'kok', 'lenn', 'lgv', 'loog', 
                  'maj', 'mat', 'med', 'mer', 'kunst,' 'meteor', 'mets', 'miner', 'muus', 'mäend', 'müt', 'paleont', 
                  'ped', 'pol', 'psühh', 'põll', 'relig', 'sotsiol', 'stat', 'sõj', 'sport', 'zool', 'tants', 'tehn', 'tekst', 
                  'trük', 'vet', 'ökol']
    while True:
        valdkond = valdkonnad[random.randint(0, len(valdkonnad)-1)]
        sobivadSõnad = leiaSamastValdkonnast(valdkond)
        if len(sobivadSõnad) > 6:
            break
    # võtame sõnad kergete seast, sest laused on hetkel ainult kergetele olemas
    sõnad = []
    vastus = []
    sõna = sobivadSõnad[random.randint(0, len(sobivadSõnad)-1)]
    sõnad.append(sõna)
    for i in range(5):
        while True:
            sõna = sobivadSõnad[random.randint(0, len(sobivadSõnad)-1)]
            if sõna not in sõnad:
                sõnad.append(sõna)
                break
        lauseOsad = laused[sõna][random.randint(0, len(laused[sõna]) - 1)]
        lauseOsad[0] = lauseOsad[0].replace("<p>", "")
        lauseOsad[1] = lauseOsad[1].replace("</p>", "")
        lauseOsad[-1] = lauseOsad[-1].replace("-", "")
        lause = {"sõna": [sõna, lauseOsad[-1]], "vasak": lauseOsad[0], "parem": lauseOsad[1], "sõnad": sõnad}
        vastus.append(lause)
        i+=1
    return vastus

if __name__ == "__main__":
    app.run(debug=True)