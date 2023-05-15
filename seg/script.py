import os
import json
import time

RESULTADO_SEM_INTERNET = ";; connection timed out; no servers could be reached  "
STATUS_SEM_INTERNET = "status sem internet"

def lerLista(lista):
    lines = []
    with open(lista, 'r') as file:
        for line in file:
            lines.append(line.strip())
    return lines

def lerSave(arquivo):
    f = open(arquivo + ".txt", "r")
    return int((f.read()))
    
def escreverResultado(string,arquivo):
    with open(arquivo + '.txt', 'a') as f:
        f.write(string + "\n")

def salvarLinha(linha,arquivo):
    with open(arquivo + '.txt', "w") as f:
        f.write(str(linha))
       
def validaSites(sites):
    contSites = 0
    for site in sites:
        time.sleep(1)
        contSites += 1
        cmd = 'dig +short +noall +answer ' + site + " @9.9.9.10 | tr '\n' ' '"
        text = os.popen(cmd)
        res = text.read()
        
         #internet check
        if (res == RESULTADO_SEM_INTERNET):
            res = internetLock(res,cmd,RESULTADO_SEM_INTERNET)
        
        resultado = '{"site" : "' + site + '" , "resposta" : "' + res + '"}'
        print(resultado)
        # verifica internet
        # if (resultado == RESULTADO_SEM_INTERNET):
        #          resultado = internetLock(resultado,cmd,RESULTADO_SEM_INTERNET)
        
        #verifica validade do resultado
        if res:
            escreverResultado(resultado,'sitesValidados')
        else:
            escreverResultado(resultado,'sitesInvalidos')
        #verifica se tem internet
        if (res == ";; connection timed out; no servers could be reached  "):
            raise Exception('Sem internet')
        salvarLinha(contSites, 'saveSitesValidados')

def atualizaDNS(dns):
   
    with open('contagemDNS.txt', 'r+') as f:
        
        linhas = f.readlines()
        for i, linha in enumerate(linhas):
            ip, contador = linha.strip().split('-')
            if ip == dns:
                novo_contador = int(contador) + 1
                linhas[i] = f"{dns}-{novo_contador}\n"
                f.seek(0)
                f.writelines(linhas)
                return True
        # Se o DNS não foi encontrado, retorna False
        return False

def internetLock(resultado,cmd,semInternet):
    if (semInternet == STATUS_SEM_INTERNET):
        while(resultado.isspace()):
            #cmd = "dig +short " + jsonSite['site'] + " @" + dns + " | tr '\n' ' '  "
            time.sleep(1)
            text =  os.popen(cmd)
            resultado = text.read()
            print("status: " + resultado)
    else:
        
        while (resultado == semInternet):
            #cmd = "dig +short " + jsonSite['site'] + " @" + dns + " | tr '\n' ' '  "
            time.sleep(1)
            text =  os.popen(cmd)
            resultado = text.read()
            print(resultado)
    return resultado

def testaDns(dnss,sites):
    contSites = 0
    for site in sites:
        contDNS = 0
        contSites += 1
        for dns in dnss:
            time.sleep(1)
            contDNS += 1
            jsonSite = json.loads(site)
            cmd = "dig +short " + jsonSite['site'] + " @" + dns + " | tr '\n' ' '  "
            text =  os.popen(cmd)
            resultado = text.read()
            # teste = "result(dns: " + dns + ")(site: " + jsonSite['site'] + ") :\n" + resultado
            # print(teste)

            #internet check
            if (resultado == RESULTADO_SEM_INTERNET):
                 resultado = internetLock(resultado,cmd,RESULTADO_SEM_INTERNET)
                ###raise Exception('Sem internet')
            
            #status 
            cmd2 = "dig +noall +comments " +  jsonSite['site'] + " @" + dns + ' | sed -n 2p | sed \'s/.*status: //\' | cut -d "," -f1'
            text2 =  os.popen(cmd2)
            status = text2.read()
            #print("status :" + status)
          
            #internet check 2 
            if status.isspace():
                status = internetLock(status,cmd2,STATUS_SEM_INTERNET)

            #checar status
            if ("NOERROR" not in status):
                atualizaDNS(dns)
                print(jsonSite['site'] + "(" + dns + ")")
                
            #checar 0.0.0.0    
            if (resultado.strip().startswith("0.0.0.0")):
                atualizaDNS(dns)
                print(jsonSite['site'] + "(" + dns + ")")
                
            #checar dns (208.67.222.123)   
            if (resultado.strip().startswith("146.112.61.106")):
                atualizaDNS(dns)
                print(jsonSite['site'] + "(" + dns + ")")
            
            #checar adguardplus (176.103.130.132)
            if (resultado.strip().startswith("176.103.130.135")):
                atualizaDNS(dns)
                print(jsonSite['site'] + "(" + dns + ")")
            
            #check yandex ()
            if (resultado.strip().startswith("safe2.yandex.ru. 93.158.134.250")):
                atualizaDNS(dns)
                print(jsonSite['site'] + "(" + dns + ")")
            

            # print(resultado)
            #escreverResultado(resultado,'result')
            # print(jsonSite['site'] + "(" + dns + ")")
            # print("sem DNS: " + jsonSite['resposta'])
            # print("com DNS: " + resultado)
            # print("\n")
            # if (jsonSite['resposta'] != resultado):
            #     print(resultado)
            #     atualizaDNS(dns)
            
            salvarLinha(contDNS,"saveDNS") 
        salvarLinha(contSites,'saveSite')
        

dnss = lerLista("dns.txt")
sites = lerLista("sites.txt")
#testaDns(dnss,sites)
#lerSave('saveSite')

#validaSites(sites)

sitesValidados = lerLista("sitesValidados.txt")

testaDns(dnss,sitesValidados)