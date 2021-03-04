# ShareDoc
Made with Flask and SQLite3, ShareDoc is a website taht allows users to create documents that can be set to private or set to public where anyone can view them.

## How to Use 
The main thing about ShareDoc is to create... well, docs/documents. To create one, click the small button that the left side of the screen that says `Create New Doc`. Enter a title, your author name, then a password you will remember for when you need to update your document. Then, you may start typing. 

## Features
Some features when writing your doc is the @ function and the # functions. At the end of your document, you can tag something that is related to the content of your doc. For example, `#Cool` or `#ShareDoc`. The @ function allows you to 'ping' people. It doesn't actually ping, but when you mention a user or another author on ShareDoc you can put their name in that form. For example, `@Jonathan2018` or `@AquaMarine`. When your doc is published, it will render the pings and tags differently. They are also clickable when they are rendered. When you click the tags, ShareDoc will search for other docs on the site that have titles related to that tag. When you click on pings, ShareDoc will search for other docs that were made by that author and related authors.

## How it Works
When you create a document and save it, ShareDoc logs the content of your doc, the author, hashes your password, and whether your doc it public or private. And ShareDoc will put them into a SQLite3 database. ShareDoc will only index the public docs and put them on the main page. The private docs are for you to store your secrets. 
