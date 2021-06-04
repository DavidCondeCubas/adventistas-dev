odoo.define('adm.application.documents', require => {
    "use strict";
    require('web.core');
    const rpc = require('web.rpc');
    const {fileList} = require('adm.form.common');

    $(document).ready(() => {
        /*
        We want to preview images, so we need to register the Image Preview plugin
        */
        FilePond.registerPlugin(
            FilePondPluginFileEncode,
            FilePondPluginFileValidateSize,
            FilePondPluginImagePreview
        );

        // Select the file input and use create() to turn it into a pond
        $('[data-adm-model-fields="1"] input[type="file"]').each((i, el) => {
            const admField = el.dataset.admField;
            const f = FilePond.create(el, {
                onupdatefiles: function(files) {
                    fileList[admField] = files;
                    console.log(files);
                },
                options: {
                    type: 'local',

                    // mock file information
                    file: {
                        name: 'my-file.png',
                        size: 3001025,
                        type: 'image/png'
                    }
                }
            });
            f.element.dataset.admField = el.dataset.admField;
            f.element.dataset.admFileAttIds = el.dataset.admFileAttIds;

            if (el.dataset.admFileAttIds) {
                const attIds = JSON.parse(f.element.dataset.admFileAttIds);
                rpc.query({
                    method: 'read',
                    model: 'ir.attachment',
                    args: [attIds],
                    kwargs: {
                        fields: ['name', 'mimetype', 'id', 'file_size']
                    }
                }).then(result => {
                    _.each(result, fileRes => {
                        f.addFile(fileRes.name, {
                            type: 'local',
                            file: {
                                name: fileRes.name,
                                size: fileRes.file_size,
                                type: fileRes.mimetype,
                            },
                            metadata: {
                                id: fileRes.id
                            }
                        });
                    });
                });
            }
        });
    })
});