r"""
Installed product IDs
=====================

InstalledProductIDs - command ``find /etc/pki/product-default/ /etc/pki/product/ -name '*pem' -exec rct cat-cert --no-content '{}' \;``
---------------------------------------------------------------------------------------------------------------------------------------

This module provides a parser for information about certificates for
Red Hat product subscriptions.

"""
from insights.core.filters import add_filter
from insights.specs import Specs
from .. import parser, CommandParser

add_filter(Specs.subscription_manager_installed_product_ids, ['ID:', 'Product Certificate', 'Path:'])


@parser(Specs.subscription_manager_installed_product_ids)
class InstalledProductIDs(CommandParser):
    r"""
    Parses the output of the comand::

        find /etc/pki/product-default/ /etc/pki/product/ -name '*pem' -exec rct cat-cert --no-content '{}' \;

    Sample output from the unfiltered command looks like::

        +-------------------------------------------+
        Product Certificate
        +-------------------------------------------+

        Certificate:
            Path: /etc/pki/product-default/69.pem
            Version: 1.0
            Serial: 12750047592154749739
            Start Date: 2017-06-28 18:05:10+00:00
            End Date: 2037-06-23 18:05:10+00:00

        Subject:
            CN: Red Hat Product ID [4f9995e0-8dc4-4b4f-acfe-4ef1264b94f3]

        Issuer:
            C: US
            CN: Red Hat Entitlement Product Authority
            O: Red Hat, Inc.
            OU: Red Hat Network
            ST: North Carolina
            emailAddress: ca-support@redhat.com

        Product:
            ID: 69
            Name: Red Hat Enterprise Linux Server
            Version: 7.4
            Arch: x86_64
            Tags: rhel-7,rhel-7-server
            Brand Type:
            Brand Name:


        +-------------------------------------------+
            Product Certificate
        +-------------------------------------------+

        Certificate:
            Path: /etc/pki/product/69.pem
            Version: 1.0
            Serial: 12750047592154751271
            Start Date: 2018-04-13 11:23:50+00:00
            End Date: 2038-04-08 11:23:50+00:00

        Subject:
            CN: Red Hat Product ID [f3c92a95-26be-4bdf-800f-02c044503896]

        Issuer:
            C: US
            CN: Red Hat Entitlement Product Authority
            O: Red Hat, Inc.
            OU: Red Hat Network
            ST: North Carolina
            emailAddress: ca-support@redhat.com

        Product:
            ID: 69
            Name: Red Hat Enterprise Linux Server
            Version: 7.6
            Arch: x86_64
            Tags: rhel-7,rhel-7-server
            Brand Type:
            Brand Name:

    Filters have been added to the parser so that only the filtered lines will be collected.

    Attributes:
        ids (set): set of strings of the unique product IDs
        product_certs(list): list of dicts of the product certificates key-value pairs split by colon,
            the key is transferred to lowercase format concatenated by an underscore if it contains whitespace

    Examples:
        >>> type(products)
        <class 'insights.parsers.installed_product_ids.InstalledProductIDs'>
        >>> list(products.ids)
        ['69']
        >>> products.product_certs[0]
        {'path': '/etc/pki/product-default/69.pem', 'id': '69'}

    """
    def parse_content(self, content):
        """ Parse command output """
        self.ids = set()
        self.product_certs = []
        one_file_data = None
        for line in content:
            line = line.strip()
            # different file delimiter
            if line == 'Product Certificate':
                if one_file_data:
                    self.product_certs.append(one_file_data)
                one_file_data = {}
            elif one_file_data is not None and ':' in line:
                name, value = line.split(':', 1)
                lower_name_with_underscore = '_'.join([item.strip().lower() for item in name.split()])
                one_file_data[lower_name_with_underscore] = value.strip()
        if one_file_data:
            # add the last file data
            self.product_certs.append(one_file_data)
        self.ids = set([item['id'] for item in self.product_certs])
