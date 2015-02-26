App.filter('timeAgo', function() {
    var offset = moment().zone();

    return function(input) {
        if (!input) return '';
        return moment.utc(input).zone(offset).fromNow();
    };
}).filter('formatDate', function() {
    var offset = moment().zone();

    return function(input) {
        if (!input) return '';
        return moment.utc(input).zone(offset).format('MMMM D, YYYY');
    };
}).filter('joinList', function() {
    return function(input, separator) {
        if (!input) return '';
        return input.join(separator || ', ');
    };
}).filter('currencyType', function() {
    return function(input) {
        return parseFloat(input).toFixed(2).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    };
}).filter('floatType', function() {
    return function(input) {
        return parseFloat(input).toFixed(2).toString();
    };
}).filter('budgetRange', function() {
    return function(input) {
        var lim = input.split('-'), phrase = "";
        phrase += lim[0] == "0" ? "Up" : "From $" + (parseFloat(lim[0]) - 0.99).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
        phrase += lim[1] == "inf" ? " up" : " to $" + parseFloat(lim[1]).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
        return phrase;
    };
}).filter('createNewItem', function() {
    return function(input, disable) {
        return disable ? input : "<i>Create supplier "+input+"</i>";
    };
});
