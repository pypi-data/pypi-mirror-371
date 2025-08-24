import re
from googletrans import Translator
from tqdm import tqdm


def translate_and_write_file(highlighted_words, target_file_name, dest_lang='fa', deck_name=None, tags=None):
    translator = Translator()
    
    with open( target_file_name, "w", encoding="utf-8") as file:
        file.writelines('#separator:tab\n')
        file.writelines('#html:true\n') 
        file.writelines('#notetype:Basic\n')
        if deck_name != None: file.writelines('#deck column:3\n')
        if tags != None: file.writelines('#tags column:4\n')
        
        for word in tqdm(highlighted_words):
            
            preprocessed_word = re.sub("[!@#$,.%&=+/()0123456789]", '', word)

            translation_dest_lang = translator.translate(  preprocessed_word  , dest=dest_lang )
            translation_eng = translator.translate(  preprocessed_word , dest='en')

            prononc = translation_eng.extra_data['translation'][-1][-1]
            if type(prononc)!=str:
                prononc='-'

            contents_list = list()
            contents_list += ['<style>._row_{display: flex;flex-direction:column ;}@media screen and (min-width: 768px) {._row_ {display:flex;flex-direction:row;}}</style>']  #-reverse
            contents_list += ['<div><center style="font-size: 35px;"><b>' , preprocessed_word ,
                           '</b></center>  <center style="font-size: 25px;margin-top:8px;margin-bottom:13px">/',
                           prononc , '/</center></div> '] 

            contents_list += ['<div class="_row_">']
            
            # Definitions
            contents_list += ['<div style="width:100%;float:left">']
            contents_list += ['<b><center style="font-size: 24px;font-family: Copperplate;">Definitions</center></b>']
            if translation_eng.extra_data['definitions'] != None:
                for x in translation_eng.extra_data['definitions']:
                    contents_list += ['<div style="font-size:22px;font-family: Papyrus;text-align: left;direction:ltr;"><b>> ' , x[0] , ':</b></div>' ]
                    for y in x[1]:
                        contents_list += ['<div style="margin-left:30px; font-size:22px;text-align: left;direction:ltr;"><li><b>' , y[0] , '</b></li></div>']

                        if len(y)> 2 and y[2]!=None:
                            contents_list += ['<div style="margin-left:60px; font-size:20px;text-align: left;direction:ltr;"><i>' , y[2] , '</i></div>']
                    contents_list += ['<br>']

                    
            # Synonyms
            if translation_eng.extra_data['synonyms'] != None:
                contents_list += ['<br><b><center style="font-size: 24px;font-family: Copperplate;"><br>Synonyms</center></b>']
                for x in translation_eng.extra_data['synonyms']:
                    contents_list += ['<div style="font-size:22px;font-family: Papyrus;text-align: left;direction:ltr;"><b>> ' , x[0] , ':</b></div>']
                    contents_list += [ '<div style="margin-left:30px;text-align: left;direction:ltr;">']
                    contents_list += [ " - ".join(x[1][0][0]) ]
                    contents_list += ['</div><br>']
            contents_list += ['</div>']


            # Translations
            if translation_dest_lang.extra_data['all-translations'] != None:
                contents_list += ['<div style="width:100%;float:right;">']
                contents_list += ['<b><center style="font-size: 24px;font-family: Copperplate;">Translations</center></b><br>']
                contents_list += ['<table align="center"  rules="all" style="border:1.5px solid black;direction:ltr;font-size:20px;" ><tr>   <th style="text-align: center">Eng</th> <th style="text-align: center">',dest_lang,'</th>    </tr>']
                for x in translation_dest_lang.extra_data['all-translations'][0][2]:
                    contents_list += ['<tr><td style="text-align:left;direction:ltr;">' , " , ".join(x[1]) , '</td><td style="text-align:right">' ,str(x[0]) , '</td></tr>']
                contents_list += ['</table>'] 
                contents_list += ['</div>'] 
            
            contents_list += ['</div>']
            
            contents_str = "".join(contents_list)
            extra_cols = ""
            if deck_name == None: deck_name=""
            if tags==None: tags=""
            file.writelines( '<center><h1>' + preprocessed_word + '</center></h1>' + '\t' + contents_str + '\t' + deck_name+'\t' + tags  + '\n\n')