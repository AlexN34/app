/**
 * Entry point for the Angular app.
 */
var bookSwapp = angular.module('bookSwapp', [ 'ui.bootstrap', 'ngAnimate' ]);

// Changes delimiters from using {{}} to [[]]. 
// Done so that both templates w/ Jinja2 (also uses {{}} syntax) and Angular can be used
bookSwapp.config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
});

bookSwapp.controller('homeCtrl', ['$scope', '$http',
	function($scope, $http) {

		// @TODO this will be fetched from the server via an API call
		// currently is just hardcoded test data
        $http.get('/api/user/list').success(function(data) {
            $scope.users = data
        });

		$scope.listings = [
			{
				id: 1,
				name: 'Business 101',
				price: 5.00,
				location: 'UNSW',
				type: 'Wanted' // @TODO determine codes instead of string for wanted / selling / swap
			},
			{
				id: 2,
				name: 'Python Programming',
				price: 15.00,
				location: 'UTS',
				type: 'Selling'
			},
			{
				id: 3,
				name: 'Business 101',
				price: 5.00,
				location: 'Bankstown',
				type: 'Swap'
			}
		];
	}
]);
