module.exports = function(grunt) {
    var out_dir = grunt.option('dir') || 'output';

    grunt.loadNpmTasks('grunt-merge-json');

    grunt.initConfig({
        'merge-json': {
            'i18n': {
                files: {
                    'url-tree.json': [out_dir + '/*-url.json'],
                    'cname-tree.json': [out_dir + '/*-cname.json' ],
                }
            },
            'options': {
                'space': '    '
            }
        }
    });

    grunt.registerTask('default', ['merge-json']);
}
