Полное описание функций из файла

1. Класс GetFunc, который объединяет в себе все функции, которые выполняют запрос на сайт. В целом была идея (и скорее всего будет реализована) переписать этот класс
потому что многие функции выполняют лишний запрос, в функциях, в которых они вызываются. Например, получение ссылки на след страницу можно сделать по результату
функции html, но исправлять это - менять логику проги и оч много менять. Мб займусь этим.
  
  1.1 html(link) - обычный запрос на получаение html страницы
  
  1.2 next_page(link) - получение и формирование ссылки на следующую страницу по имеющейся.
  
  1.3 tables(link) - вытаскивание всех таблиц со страницы (вся инфа хранится в них)
 
  1.4 search_word_dict(link) - создается пословный словарь, каждый элемент которого содержит (слово : ссылка на страницу с характеристиками). Сделано чтоб в будущем
  вытаскивать характеристики. Ибо если делать это сразу, то все ломается из-за большого кол-ва запросов
  
  1.5 speq(words) - по словарю из 1.4 получает список кортежей - (слово, словарь характеристик). Работает долго, по аналогичной причине
  
  1.6 text(link) - используя функции выше формирует список предложений со словарями из search_word_dict
  
  1.7 page_num_fast_taker(link) - быстрая функция определенимя кол-ва страниц. Она, по сути, информативная, чтоб понимать сколько потом ждать
  
2. Класс CreatFunc, который объединяет в себе функции без запроса на сайт. Формирование ссылок, вывод в файл и ко.

2.1 info_link_creator(link, explain) - создает ссылку на страницу с характеристиками слова.

2.2 word_dict(link, table) - собсна создание пословного словаря с сылками на характеристики

2.3 tables_with_html(html) - получение таблиц без запроса (почему-то не убрал обработку нулевого ответа, потом уберу)

3. Класс CsSentences. Вот это уже именно класс, который отвечает за возможности работы с предложениями. На вход требует ссылку на результат выдачи. Дальше методы
уже как-то это обрабатывают

3.1 to_file() - печать результата в csv файл. Столбцы - |предложение|источник|омонимия|

3.2 get_sentences() - вытаскивание предложений

3.3-4 omonim_on/off() - снятая/не снятая омонимия

3.5 sent_word_speq(sent) - по предлождению получаем характеристики всех слов

4. CorporaInfo - пока не полный класс, который отвечает за характеристики самого корпуса/подкорпуса

4.1 lexem_dict - частотный список лексем

Еще, соответственно, получение лемм и ко.
В целом, можно еще сделать визуализации всего этого.
Пока, по сути, это просто куча функций, которые могут вытаскивать информацию с сайта. Не более того, что на нем есть. Просто автоматически.
Сделал, поскольку часто требовалось что-то получить из нкря, а ручками выписывать не так весело
