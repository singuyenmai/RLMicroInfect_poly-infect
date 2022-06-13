colorBook = {
    "Egypt": {
        "bla": "#262827",
        "blu": "#0f7ba2",
        "red": "#dd5129", 
        "gre": "#43b284", 
        "yel": "#fab255"
    },
    "myTheme":{
        "grey": "#919191",
        "pur": "#8D6AA0",
        "gre": "#C9B96B",
        "tur": "#17A398",
        "ora": "#FE7F2D",
        "red": "#DD614A",
        "ruby": "#A20021",
        "exp": "#9b3c96"
    }
} # Reference: https://github.com/BlakeRMills/MetBrewer
    
def get_colorBook(name):
    return colorBook[name]