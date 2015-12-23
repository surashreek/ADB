def probeDatabase(bing_key, node, URL, queryProbes, position, sample, index):
    resp = None
    jsonResult = None

    if position == 0:
        resp = bingSearch(bing_key, URL, queryProbes[position])
        jsonResult = json.loads(resp)
    else:
        query = queryProbes[position] + " NOT ( "

        # append negation of all earlier queries to obtain better accuracy and issue final query to Bing
        for i in range(position - 1):
            query = query + " " + "(" + queryProbes[i] + ") OR"
        query = query + " )"

        print "Issuing query: {}".format(query)
        resp = bingSearch(bing_key, URL, query)
        jsonResult = json.loads(resp)

    # print result and total hits for given URl
    print "Web Total hits {}".format(jsonResult['d']['results'][0]['WebTotal'])

    documents = jsonResult['d']['results'][0]['Web']

    i = 0
    for document in documents:

        try:
            if document["Url"].strip().endswith(".pdf") or document["Url"].strip().endswith(".ppt"):
                print "Skipping binary page: %s" % document["Url"]
                continue

            print "Getting page %s " % document["Url"]
            p = os.popen("lynx --dump '%s'" % document["Url"],"r")
            content = ""
            while 1:
                line = p.readline()
                if not line: break
                content = content + line

            # Clean content generated by lynx
            content = content[:content.rfind("\nReferences\n")]
            p = re.compile( '\[[^\]]*\]')
            content = p.sub('', content)

            # Update sample
            curr_node = node
            while curr_node is not None:
                if node.classification not in sample:
                    sample[curr_node.classification] = {}

                # sample[node.classification][document["Url"]] = content
                performIndexing(index, curr_node, document["Url"], content)
                curr_node = curr_node.parent

            i = i + 1

        except Exception, error:
            logging.warning("Skipping this document due to this error: '%s'" % error)

        if i >= 4:
            break

    return int(jsonResult['d']['results'][0]['WebTotal'])