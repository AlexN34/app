/**
 * Entry point for the Angular app.
 */
var bookSwapp = angular.module('bookSwapp', [ 'ui.bootstrap', 'ngAnimate' ]);

bookSwapp.controller('homeCtrl', ['$scope', '$http',
	function($scope, $http) {

		// @TODO this will be fetched from the server via an API call
		// currently is just hardcoded test data

		/*
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
		*/

		$http({
			method: 'GET',
			url: 'http://bookswapp.apps.mlux.me/api/books/list/all'
		}).then(function successCallback(response) {
			$scope.listings = response.data;
		}, function errorCallback(response) {
			console.log('Errored out: ' + JSON.stringify(response));
		});

		// Getting list of users
		$http({
			method: 'GET',
			url: 'http://bookswapp.apps.mlux.me/api/user/list'
		}).then(function successCallback(response) {
			$scope.users = response.data;
			console.log(response.data);
		}, function errorCallback(response) {
			console.log('Errored out: ' + JSON.stringify(response));
		});

		$scope.selectedType = 'selling';

		$scope.selectType = function(type) {
			$scope.selectedType = type;
		};
	}
]);
