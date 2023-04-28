tds = document.getElementsByClassName('has-events');
        var JSONData = [];
        for(var i=0; i<tds.length; i++) {
            var day = {};
            day['date'] = tds[i].getAttribute('data-date');
            items = tds[i].querySelectorAll('.event-details');
            day['events'] = [];
            items.forEach(item => {
                var e = {};
                title = item.querySelector('h5').children[0];
                time = item.querySelector('.ecwd-time').children[0];
                place = item.querySelector('.ecwd-venue').children[0].children[0];
                e['name'] = title.textContent;
                e['link'] = title.getAttribute('href');
                e['time'] = time.textContent;
                e['place'] = place.textContent;
                day['events'].push(e);
            });
            JSONData.push(day)
        }

        return JSONData