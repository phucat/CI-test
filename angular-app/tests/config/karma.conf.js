basePath = '../../';

files = [
  JASMINE,
  JASMINE_ADAPTER,
  'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
  'angular/angular.js',
  'angular/angular-*.js',
  'ferris/*.js',

  'directives.js',
  'app.js',

  'tests/mocks/**/*.js',
  'tests/*.js'
];

exclude = [
  'angular/*-min.js',
  'angular/angular-scenario*',
  'angular/angular-bootstrap-prettify*'
];

autoWatch = true;

singleRun = false;

reporters = ['progress'];

colors = true;

// browsers = ['Chrome'];
//browsers = ['C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe'];
