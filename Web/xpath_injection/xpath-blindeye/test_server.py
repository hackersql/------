from lxml import etree
from flask import Flask, request

tree = etree.parse("example.xml")
app = Flask("test_server")


@app.route("/", methods=["GET"])
def test():
    name = request.args['name']
    xpath_query = "/CATALOG/PLANT[COMMON='{}']".format(name)
    print(xpath_query)
    results = tree.xpath(xpath_query)
    print(results)
    if results:
        return "true"
    else:
        return "false"


if __name__ == "__main__":
    app.run()
