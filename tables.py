from flask_table import Table, Col, DatetimeCol


class NewsTable(Table):
    _id = Col('ID', show=False)
    newspaper = Col('Newspaper')
    title = Col('Title')
    text = Col('Text')
    tags = Col('Tags')
    link = Col('Link')
    pub_date = Col('Published')
    extract_date = Col('Extracted')
    category = Col('Category', show=False)
