/*
Copyright 2008-2009 University of Toronto

Licensed under the Educational Community License (ECL), Version 2.0 or the New
BSD license. You may not use this file except in compliance with one of these
Licenses.

You may obtain a copy of the ECL 2.0 License and BSD License at
https://source.fluidproject.org/svn/LICENSE.txt
*/

/*global jQuery*/
/*global fluid*/
/*global jqUnit*/
/*global expect*/

(function ($) {
    $(document).ready(function () {
        
        var tests = jqUnit.testCase("Decapod Capture Tests", function () {
            tests.fetchTemplate("../../../components/capture/html/Capture.html", ".flc-capture");
        });
        
        // TODO Load the options from a config file (when the model is persisted).
        var options = {
            thumbs: [
                {
                    fullImage: "../../../components/server/testData/capturedImages/Image0.jpg",
                    thumbImage: "../../../components/server/testData/capturedImages/Image0-thumb.jpg",
                    fixedImage: "../../../components/server/testData/capturedImages/Image0.jpg"
                },
                {
                    fullImage: "../../../components/server/testData/capturedImages/Image1.jpg",
                    thumbImage: "../../../components/server/testData/capturedImages/Image1-thumb.jpg",
                    fixedImage: "../../../components/server/testData/capturedImages/Image1.jpg"
                },
                {
                    fullImage: "../../../components/server/testData/capturedImages/Image2.jpg",
                    thumbImage: "../../../components/server/testData/capturedImages/Image2-thumb.jpg"
                },
                {
                    fullImage: "../../../components/server/testData/capturedImages/Image3.jpg",
                    thumbImage: "../../../components/server/testData/capturedImages/Image3-thumb.jpg"
                },
                {
                    fullImage: "../../../components/server/testData/capturedImages/Image4.jpg",
                    thumbImage: "../../../components/server/testData/capturedImages/Image4-thumb.jpg"
                }
            ],
            serverOn: false,
            cameraOn: false
        };
        
        /**
         * Tests if the component is initialized properly. The containers for 
         * the Capture and ImageReorderer should be set correctly. Model should
         * not be undefined or null.
         * 
         * @param {Object} component, the Capture component to be tested
         */
        var testComponentConstruction = function (component) {
            jqUnit.assertNotUndefined("Model is not undefined", component.model);
            jqUnit.assertNotNull("Model is not null", component.model);
        };
        
        /**
         * Tests whether the preview area correctly represents the currently
         * selected thumbnail item.
         * 
         * @param {Object} component, the Capture component to be tested
         * @param {Object} thumbItem, the selected item which should be
         *                  displayed full-sized in the preview area.
         */
        var testPreview = function (component, thumbItem) {
            var fullSrc;
            var itemIndex = component.locate(("itemIndex"), thumbItem).text() - 1;
            if (component.model.length !== 0) {
                fullSrc = component.model[itemIndex].fullImage;
            }
            var imagePreview = component.locate("imagePreview");
            
            jqUnit.assertEquals("Image in preview is", fullSrc, $(imagePreview).attr('src'));
        };
        
        /**
         * Test that there is only one delete button on the page (the one of the
         * selected thumbnail).
         * 
         * @param {Object} component, the Capture component to be tested
         * @param {Object} item, the currently selected item
         */
        var testDeleteButtons = function (component) {
            var delButtonsCount = $(':visible', component.locate("deleteButton")).length;
            jqUnit.assertEquals("Visible delete buttons on page are", 1, delButtonsCount);
        };
        
        /**
         * Tests that the state of the 'Fix image' and 'Compare before/after'
         * buttons is correct. Only one of them should be enabled according to
         * the state of the selected image (whether it is fixed or not).
         * 
         * @param {Object} component, the Capture component to be tested
         */
        var testButtonState = function (component) {
            var isFixed = component.model[component.selectedItemIndex].isFixed;
            var fixClass = component.locate("fixButton").hasClass("ui-state-disabled");
            var compareClass = component.locate("compareButton").hasClass("ui-state-disabled");
            if (isFixed) {
                jqUnit.assertTrue("Fix button state is correct.", fixClass);
                jqUnit.assertFalse("Compare button state is correct.", compareClass);
            } else {
                jqUnit.assertFalse("Fix button state is correct.", fixClass);
                jqUnit.assertTrue("Compare button state is correct.", compareClass);
            }
        };
        
        /**
         * Tests whether the indices of the thumbnails are in the correct order
         * and that the markup is synced with the model.
         * 
         * @param {Object} component, the Capture component to be tested.
         */
        var testIndices = function (component) {
            var allIndices = component.locate("itemIndex");
            jqUnit.assertEquals("Number of item indices are", component.model.length, allIndices.length);
            allIndices.each(function (index, item) {
                jqUnit.assertEquals("Current item has index", index + 1, $(item).text());
            });
        };
        
        tests.test("Component construction with no model", function () {
            expect(6);
            
            var capture = fluid.capture(".flc-capture");
            var thumbItems = capture.locate("thumbItem");
            testComponentConstruction(capture);
            
            jqUnit.assertEquals("Model length is", 0, capture.model.length);
            jqUnit.assertEquals("Image items on page are", 1, thumbItems.length);
            
            jqUnit.assertTrue("Fix button is disabled.", capture.locate("fixButton").hasClass("ui-state-disabled"));
            jqUnit.assertTrue("Compare button is disabled.", capture.locate("fixButton").hasClass("ui-state-disabled"));
        });
        
        tests.test("Component construction with a sample model", function () {
            expect(9 + options.thumbs.length);
            
            var capture = fluid.capture(".flc-capture", options);
            var thumbItems = capture.locate("thumbItem");
            testComponentConstruction(capture);
            
            jqUnit.assertEquals("Model length is", options.thumbs.length, capture.model.length);
            jqUnit.assertEquals("Image items on page are", capture.model.length, thumbItems.length);
            
            testPreview(capture, thumbItems[thumbItems.length - 1]);
            testIndices(capture);
            testDeleteButtons(capture);
            testButtonState(capture);
        });
        
        tests.test("UI update on image selection", function () {
            expect(9);
            
            var capture = fluid.capture(".flc-capture", options);
            var thumbItems = capture.locate("thumbItem");
            var firstItem = thumbItems[0];
            var secondItem = thumbItems[1];
            
            testDeleteButtons(capture);
            
            $(firstItem).click();
            testPreview(capture, firstItem);
            testDeleteButtons(capture);
            testButtonState(capture);
            
            $(secondItem).click();
            testPreview(capture, secondItem);
            testDeleteButtons(capture);
            testButtonState(capture);
        });
        
        tests.test("Thumbnail deletion", function () {
            expect(8 + options.thumbs.length);
            
            var capture = fluid.capture(".flc-capture", options);
            var currentLength = options.thumbs.length;
            var thumbItems = capture.locate("thumbItem");
            $(thumbItems[0]).focus();
            var deleteButton = $(':visible', capture.locate("deleteButton"));
            var itemToBeSelected = thumbItems[1];
            
            jqUnit.assertEquals("Model length before deletion is", currentLength, capture.model.length);
            jqUnit.assertEquals("Images on page before deletion are", currentLength, thumbItems.length);
            
            deleteButton.click();
            thumbItems = capture.locate("thumbItem");
            testIndices(capture);
            
            jqUnit.assertEquals("Model length after deletion is", currentLength - 1, capture.model.length);
            jqUnit.assertEquals("Images on page after deletion are", currentLength - 1, thumbItems.length);
            
            testPreview(capture, itemToBeSelected);
            testDeleteButtons(capture);
            
            currentLength = thumbItems.length;
            $(thumbItems[currentLength - 1]).focus();
            deleteButton = $(':visible', capture.locate("deleteButton"));
            itemToBeSelected = thumbItems[currentLength - 2];
            
            deleteButton.click();
            testPreview(capture, itemToBeSelected);
            testDeleteButtons(capture);
        });
        
        tests.test("Taking pictures", function () {
            expect(3);
            
            var capture = fluid.capture(".flc-capture", options);
            var thumbItems;
            
            var takePictureButton = capture.locate("takePictureButton");
            
            takePictureButton.click();
            thumbItems = capture.locate("thumbItem");
            
            jqUnit.assertEquals("Model length after first picture taken", options.thumbs.length + 1, capture.model.length);
            jqUnit.assertEquals("Images on page after first picture taken", capture.model.length, thumbItems.length);
            testPreview(capture, thumbItems[thumbItems.length - 1]);
        });
        
        tests.test("Deleting the last image left", function () {
            expect(3);
            
            var capture = fluid.capture(".flc-capture", {
                thumbs: [
                    {
                        fullImage: "../../../components/server/testData/capturedImages/Image0.jpg",
                        thumbImage: "../../../components/server/testData/capturedImages/Image0-thumb.jpg"
                    }
                ]
            });
            
            var deleteButton = $(':visible', capture.locate("deleteButton"));
            deleteButton.click();
            
            var thumbItems = capture.locate("thumbItem");
            jqUnit.assertEquals("Model length is", 0, capture.model.length);
            jqUnit.assertEquals("Image items on page are", 1, thumbItems.length);
            
            $(thumbItems[0]).click();
            var delButtonsCount = $(':visible', capture.locate("deleteButton")).length;
            jqUnit.assertEquals("Delete buttons on page are", 0, delButtonsCount);
        });
    });
    
})(jQuery);