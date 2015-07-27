from nose.plugins.attrib import attr, AttributeSelector


critical = attr(priority='critical')
major = attr(priority='major')
minor = attr(priority='minor')


class AttributeSelector(AttributeSelector):
    def configure(self, options, config):
        super(AttributeSelector, self).configure(options, config)
        self.enabled = True

    def validateAttrib(self, method, cls=None):
        """If no attrib provided - let all tests be ok to run
        """
        result = super(AttributeSelector, self).validateAttrib(method, cls)
        if result is False and not self.attribs:
            return None

        return result
