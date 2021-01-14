function Redirect(q_string) {
    var path_mapper = ['/chara','/scene','/housing'];
    var q_op = (q_string.indexOf('+')!=-1)?'+':((q_string.indexOf('*')!=-1)?'*':'-');
    var [q_target,q_value] = q_string.split(q_op);
    q_value = Number(q_value);
    var protocol = 'https';
    var host = window.location.host;
    var path = window.location.pathname;
    var query = window.location.search;
    var s = new Map();
    
    if(query.length!=0){
        s = getUrlParams(query);
    }
    
    if(!s.has('page')){
        s.set('page',[1]);
    }
    if(!s.has('lang')){
        s.set('lang',[0]);
    }
    if(!s.has('order')){
        s.set('order',[0]);
    }
    if(!s.has(q_target)){
        s.set(q_target,[]);
    }
    if(q_target=='cat'){
        if(q_op=='*'){
            s = new Map([['lang',s.get('lang')]]);
            path  = path_mapper[q_value];
        }
    }
    else if(q_target=='uploader_uuid'){
        if(q_op=='*'){
            s = new Map([['lang',s.get('lang')],['uploader_uuid',[q_value]]]);
        }
    }
    else if((new Set(['order','page','lang'])).has(q_target)){
        if(q_op=='*'){
            s.set(q_target,[q_value]);
        }
        else if(q_op=='+'){
            s.set(q_target,[s.get(q_target)[0]+q_value]);
        }
        else if(q_op=='-'){
            if(s.get(q_target)[0]>1){
                s.set(q_target,[s.get(q_target)[0]-q_value]);
            }
        }
    }
    else{
        if(!s.get(q_target).includes(q_value)){
            if(q_op=='+'){
                s.get(q_target).push(q_value);
            }
        }else{
            if(q_op=='-'){
                s.get(q_target).splice(s.get(q_target).indexOf(q_value),1);
            }
        }
    }
    if(!(new Set(['page','lang'])).has(q_target)){
        s.set('page',[1]);
    }
    var target_q_string = Array.from(s).map(e => {
        var [k,v] = e;
        return k+'='+v.join('.');
    }).join('&');
    window.location = protocol+'://'+host+path+'?'+target_q_string
}

function getUrlParams(search) {
    var hashes = search.slice(search.indexOf('?') + 1).split('&').filter(s=>s.substr(s.length-1)!='=');
    var params = hashes.map(hash => {
        var [key, val] = hash.split('=');
        val = val.split('.').map(Number);
        return [key, val];
    });
    return new Map(params);
}

function download_data(filename) {
    var target = '';
    if(filename.includes('chara')){
        target = '/' + filename;
    }else if(filename.includes('scene')){
        target = '/' + filename;
    }else if(filename.includes('housing')){
        target = '/' + filename;
    }
    fetch(target).then(res => res.blob().then(blob => {
        var a = document.createElement('a');
        var url = window.URL.createObjectURL(blob);
        a.href = url;
        a.download = filename;
        a.click();
        window.URL.revokeObjectURL(url);
    }))
}