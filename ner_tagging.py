from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize
import os
java_path = r'C:\Program Files\Java\jdk-10.0.1\bin\java.exe'
os.environ['JAVAHOME'] = java_path

#################################
# TODO think about how  glue entities of more than 2 tokens together
# TODO improve formatation of .xml result (punctuation marks)
# TODO test with texstep
#################################

class TokenStringBuilder:
    """
    Simple helper class for building the String represenation of the tagged tokens.
    Used for rebuilding the text with tags as xml-tags.
    """
    def __init__(self, token, **kwargs):
        if len(token) != 2: 
            raise IndexError('Arg token had wrong index! Needs to be two')
        if not all(isinstance(i, str) for i in token):
            raise TypeError('All values in arg token have to of type {}'.format(type(str)))
        
        self.token = token
        self.string = token[0]
        self.tag = token[1]

        if 'following_entity' in kwargs:
            if self.tag != kwargs['following_entity'][1]:
                raise BaseException("Following entity has to have the same tag as self.") 
            self.following_entity = TokenStringBuilder(kwargs['following_entity'])

    def to_string(self):
        if self.tag == 'O':
            if self._is_punctuation_mark(self.string):
                # TODO test the distribution of marks
                # TODO refactoring
                if self.string in ':,;.?!' or self.string == '...':
                    return self.string + " "
                if self.string in '-':  # maybe irrelevant
                    return " " + self.string + " " 
            else:
                return " " + self.string
        
        if hasattr(self, 'following_entity'):
            return ' <{tag}>{self_string} {following_string}</{tag}> '.format(
                tag=self.tag,
                self_string= self.string,
                following_string = self.following_entity.string
                )
        
        return ' <{tag}>{self_string}</{tag}> '.format(
            tag=self.tag,
            self_string= self.string
            )

                
    def _is_punctuation_mark(self, char: str):
        return char in '.?!_-:;""'
    
    def __str__(self):
        return self.to_string()
    
    def __repr__(self):
        string = str(self.token)
        if hasattr(self, 'following_entity'):
            string += '| Foll: ' + str(self.following_entity)
        return string
    
            
            



if __name__ == '__main__':
    # Change the path according to your system
    stanford_classifier = r'C:\Users\Lennart\NER Texstep\stanford-ner-2018-02-27\classifiers\dewac_175m_600.crf.ser.gz'
    stanford_ner_path = r'C:\Users\Lennart\NER Texstep\stanford-ner-2018-02-27\stanford-ner.jar'
    tagger = StanfordNERTagger(stanford_classifier, stanford_ner_path, encoding='utf-8')

    with open('buddenbrooks.txt', 'r', encoding='UTF-8') as f:
        text = f.read()


    tokenized_text = word_tokenize(text)
    classified_text = tagger.tag(tokenized_text)

    with open('tagged.txt', 'w', encoding='UTF-8') as f:
        for i in classified_text:
            f.write(str(i)+'\n')

    # restore the text and add

    # restored_text = str()
    # pass_next = False
    # for c, i in enumerate(classified_text):
    #     if pass_next:
    #         pass_next = False
    #         continue
    #     else:
    #         if i[1] != 'O':
    #             restored_text += '<{1}>{0}</1> '.format(i[0], i[1])
    #             pass_next = False
    #         try:
    #             classified_text[c+1]
    #         except IndexError:
    #             break
    #         if i[1] == 'I-PER' and classified_text[c+1][1] == 'I-PER':
    #             restored_text += '<{1}>{0}</{1}> '.format(i[0] +  " " + classified_text[c+1][0], i[1])
    #             pass_next = True
    #         else:
    #             if i[0] in ",.?!" and classified_text[-1][0] not in ",.?!":
    #                 restored_text[-1] = i[0] + " "
    #                 pass_next = False
    #             else:
    #                 restored_text += i[0] + " "
    #                 pass_next = False


    # with open('restored.xml', 'w', encoding='UTF-8') as f:
    #     f.write('<text>'+restored_text+'</text>')
    restored_text = ''
    skip_next_it = False
    for i, t in enumerate(classified_text):
        if skip_next_it:
            skip_next_it = False
            continue
        # ensure that look-forwards don't raise IndexOutOfBounds Error
        if i < len(classified_text) - 1:
            if t[1]!= 'O' and t[1] == classified_text[i+1][1]:
                tsb = TokenStringBuilder(t, following_entity=classified_text[i+1])
                skip_next_it = True
            else:
                tsb = TokenStringBuilder(t)
        else:
            tsb = TokenStringBuilder(t)
        
        restored_text += str(tsb)
    
    with open('restored.xml', 'w', encoding='UTF-8') as f:
        f.write(restored_text)
                
            
            
        
