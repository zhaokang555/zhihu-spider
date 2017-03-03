'use strict';
let cheerio = require('cheerio')
let fs = require('fs')

const id = process.argv[2]
// const b = process.argv[3]


let data = fs.readFileSync('temp/'+id+'/1.html').toString()
let $ = cheerio.load(data);

let arr = []
let row = {}
$('#zh-profile-activity-page-list').find('.zm-profile-section-item').each(function(index, el) {
    row = {}

    // 1
    row.action_time_sec = parseInt($(el).attr('data-time'))

    // 2
    // let titleTxt = $(el).find('.zm-profile-activity-page-item-main').text()
    let titleTxt = $(el).children('div').eq(0).text()
    let actionArr = titleTxt.trim().split('\n')[0].split(' ')
    // console.log(actionArr)
    let newActionArr = []
    for (let e of actionArr) 
        if (e) newActionArr.push(e)
    newActionArr.shift()
    row.action = newActionArr.join(' ')
    
    // 3
    let titleArr = $(el).children('div').eq(0).find('a').last().text().split('\n')
    row.title = titleArr.join('')
    // titleArr.shift()
    // row.title = titleArr.join('')

    // 4
    let contentDiv = $(el).children('div').eq(1)
    // console.log(contentDiv.attr('class'))
    let innerContentDiv = contentDiv.children('div').eq(1)
    // console.log(innerContentDiv.attr('class'))
    row.content = innerContentDiv.find('textarea').val()
    // console.log(row.content.length)

    arr.push(row)
    // console.log(row)
})
// console.log(arr)


let txt = JSON.stringify(arr, null, 4)
fs.writeFile('temp/'+id+'/2.json', txt,  function(err) {
   if (err) {
       return console.error(err);
   }
});




