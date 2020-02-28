Vue.filter('truncatewords', function (value, len) {
    if (!value) return 'Здесь пока пусто';
    value = value.toString().split(" ");
    return value.slice(0, len).join(' ') + '...'

});

new Vue({
        el: '#list_book',
        data: {
            books: [],
        },
        created: function () {
            const vm = this;
            axios.get('/api/v1/list_book')
                .then(function (response) {
                    vm.books = response.data;
                })

        }
    }
);

new Vue({
    el: '#book_description_',
    data: {
        show: true
    },
    methods: {
        mouseover: function(event){
          this.el = this.el + event.target.id
        },
        mouseleave: function(event){
          this.el = '#book_description_'
        }
    }

});

