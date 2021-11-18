odoo.define('bprk_portal_extended.websitemenu', function (require) {
    'use strict';

    require('web.dom_ready');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var Dialog = require('web.Dialog');
    var _t = core._t;

    Dropzone.autoDiscover = false;

    $(document).on("change", "#product_id", function(e) {
        $('#product_id').removeClass("mandatory-field");
        $("#mandatory_gross_price_div").addClass("d-none");
        $('.suppliers-list').empty();

        $('.net-price').empty();
        $('.tax-data').empty();
        $('.amount-tax').empty();
        $('.gross-price').empty();

        $('.net-price').append("0");
        $('.amount-tax').append("0");
        $('.gross-price').append("0");
        
        $("#net_price").val(0);
        $("#tax_data").val("");
        $("#amount_tax").val(0);
        $("#gross_price").val(0);


        if ($("#product_id").val()){
            var content = ""
            rpc.query({
                model: 'product.product',
                method: 'get_product_suppliers',
                args: [$("#product_id").val()],
            }).then(function(res) {
                content += "<table class='table'>"
                content += "<thead>"
                content += "<th class='text-left'>Supplier Name</th>"
                content += "<th class='text-left'>Quantity</th>"
                content += "<th class='text-left'>Net Price</th>"
                content += "<th class='text-left'>Select Any</th>"
                content += "</thead>"
                content += "<tbody>"
                content += res
                content += "</tbody>"
                content += "</table>"
                $('.suppliers-list').append($(content));
                   
            });


            
        }
    });

    $(document).on("click", ".btn_request_product", function(ev) {
        var flag = 1;
        if (!$('#product_id').val()) {
            flag = 0;
            $('#product_id').addClass("mandatory-field");
        }
        if ($('#gross_price').val() <= 0){
            flag = 0;
            $("#mandatory_gross_price_div").removeClass("d-none");
        }
        // if (!$('#attachment_id').val()){
        //     flag = 0;
        //     $("#mandatory_attachment_div").removeClass("d-none");
        // }
        if (flag == 1){

            rpc.query({
                model: 'res.users',
                method: 'check_request_rejected_date',
                args: [],
            }).then(function(res) {
                if (res) {

                    var wizard_values = '<strong>Do you want to proceed with the following data?</strong>'
                    wizard_values += "<div class='row mt-3'>"
                    wizard_values += "<div class='col-12 mt-2'>"
                    wizard_values += "<strong>PRODUCT : </strong>" + $("#product_id").children("option:selected")[0].label
                    wizard_values += "</div>"
                    wizard_values += "<div class='col-12 mt-2'>"
                    wizard_values += "<strong>GROSS PRICE : </strong>" +$("#gross_price").val() + "€";
                    wizard_values += "</div>"
                    wizard_values += "</div>"

                    new Dialog(this, {
                        title: _t('Confirmation'),
                        buttons: [
                            {
                            text: _t('Ok'), classes: 'btn-primary', close: true, click: function () {
                                $('#btn_request_product').addClass('btn-disable');
                                $('#create_request_process_icon').removeClass('d-none');
                                $("#register_form").submit()
                                }
                            },
                            {
                            text: _t('Cancel'), classes: 'btn-secondary', close: true, click: function () {
                             this.close()
                                }
                            }],
                    $content: $('<div class="form_desc">').append(wizard_values),
                    }).open()

                }

                else {
                    $("#rejected_request_warning").removeClass("d-none");
                }
                
                   
            });
        }
        

    });

    $(document).on("keyup", "#ProductRequestSearch", function(e) {
        var input, filter;
        input = document.getElementById("ProductRequestSearch");
        filter = input.value.toUpperCase();

        $(document).find(".product-request-tbody tr").each(function() {
            var order_number = $(this).children('td:first')[0].innerText;
            var state = $(this).find("td:eq(1)")[0].innerText;
            var date = $(this).find("td:eq(2)")[0].innerText;

            if ((order_number.toUpperCase().indexOf(filter) > -1) || (state.toUpperCase().indexOf(filter) > -1) || (date.toUpperCase().indexOf(filter) > -1)) {
                $(this).removeClass("d-none");
            }
            else{
                $(this).addClass("d-none");

            }
        })
    });

    $(document).on("click", ".product-request-tbody tr", function(ev) {
        var request_id = $(this).data("record-id");
        if (request_id) {
            var url = "/my/productrequest/"+ request_id
            window.location.href = url
        }

    });

    $(document).on("click", ".suppliers-list input", function(ev) {
        var supplier_id = $(this).val();
        rpc.query({
            model: 'product.product',
            method: 'get_product_prices',
            args: [supplier_id],
        }).then(function(res) {
            $('.net-price').empty();
            $('.tax-data').empty();
            $('.amount-tax').empty();
            $('.gross-price').empty();


            $('.net-price').append(res['net_price']);
            $('.tax-data').append(res['tax_name']);
            $('.amount-tax').append(res['tax_amount']);
            $('.gross-price').append(res['gross_price']);


            $("#net_price").val(res['net_price']);
            $("#tax_data").val(res['tax_name']);
            $("#amount_tax").val(res['tax_amount']);
            $("#gross_price").val(res['gross_price']);
            
               
        });

    });

    

    if ($(".product-order-dropzone").length) {

        var att_count = 0;
        var myDropzone = new Dropzone(".product-order-dropzone", {maxFiles: 1,acceptedFiles: 'image/*,pdf/*',addRemoveLinks: true, timeout: 0,});

        myDropzone.on("maxfilesexceeded", function(file) {
            att_count = att_count +1;
            myDropzone.removeFile(file);
            $('#request_document_max_files').removeClass('d-none');

        });

        // myDropzone.on("error", function(file) {
        //     setTimeout(function() {
        //         att_count  = att_count + 1
        //         myDropzone.removeFile(file);
        //     }, 0);
        //     $('#wrong_files').removeClass('d-none');

        // });

        myDropzone.on("success", function(file, response) {
            att_count = att_count + 1;
            var obj = JSON.parse(response);
            $('#attachment_id').val(obj['attachment_id'])
            
        });

        myDropzone.on("removedfile", function(file) {
            if (att_count == 1){
                $('#attachment_id').val("")    
            }

            $.ajax("/remove/file/" + file.serverID, {
                type: 'POST',
                dataType: 'json',
                success: function(data) {
                },
                error: function(error) {
                }
            });

        });
        
    }


    $(document).on("click", ".approve-btn", function(ev) {
        $('.approve-btn').addClass('btn-disable');
        $('.reject-btn').addClass('btn-disable');
        $('#approve_btn_process_icon').removeClass('d-none');

    });

    $(document).on("click", ".reject-btn", function(ev) {
        $('.reject-btn').addClass('btn-disable');
        $('.approve-btn').addClass('btn-disable');
        $('#reject_btn_process_icon').removeClass('d-none');

    });

    $(document).on("click", ".buy-product-btn", function(ev) {
        $('.buy-product-btn').addClass('btn-disable');
        $('#buy_product_btn_process_icon').removeClass('d-none');

    });

    $(document).on("click", ".pickup-btn", function(ev) {
        $('.pickup-btn').addClass('btn-disable');
        $('#pickup_btn_process_icon').removeClass('d-none');

    });


});