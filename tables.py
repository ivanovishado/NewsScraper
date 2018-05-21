from flask_table import Table, Col, DatetimeCol


class NewsTable(Table):
    _id = Col('ID', show=False)
    newspaper = Col('Newspaper')
    title = Col('Title')
    text = Col('Text')
    tags = Col('Tags')
    link = Col('Link')
    pub_date = Col('Publication Date')
    extract_date = Col('Extraction Date')
    is_classified = Col('Is Classified', show=False)
    is_violent = Col('Is Violent?')
