API Documentation
=================

Collector API documentation.

Verification Request
--------------------

..  http:post:: /verification-request

    Submits a verification request for given news.

    :<form string email: requesting user email
    :<form string comment: requesting user comment
    :<form string url: news url
    :<form string text: comment about the news
    :<form image: screenshot of content to be verified

    :>json string comment: requesting user comment
    :>json uuid id: news draft id
    :>json string origin: source of verification request service
    :>json string reporter_email: requesting user email
    :>json datetime reported_at: verification request datetime
    :>json string screenshot_url: screenshot url
    :>json string url: news url
    :>json string text: comment about the news

    :statuscode 201: success
    :statuscode 400: bad request

Chatbot Verification Request
----------------------------

..  http:post:: /chatbot-verification-request

    Submits a chatbot verification request for given news.

    :<json string email: requesting user email
    :<json string question: requesting user question
    :<json string source: news url

    :>json uuid id: news draft id
    :>json string reporter_email: requesting user email
    :>json datetime reported_at: verification request datetime
    :>json string source: news url
    :>json string question: comment about the news

    :statuscode 201: success
    :statuscode 400: bad request

Mobile Verification Request
---------------------------

..  http:post:: /mobile-verification-request

    Submits a mobile verification request for given news.

    :<form string email: requesting user email
    :<form string comment: requesting user comment
    :<form string url: news url
    :<form image: screenshot of content to be verified (optional)

    :>json string comment: requesting user comment
    :>json uuid id: news draft id
    :>json string reporter_email: requesting user email
    :>json datetime reported_at: verification request datetime
    :>json string screenshot_url: screenshot url
    :>json string url: news url

    :statuscode 201: success
    :statuscode 400: bad request
