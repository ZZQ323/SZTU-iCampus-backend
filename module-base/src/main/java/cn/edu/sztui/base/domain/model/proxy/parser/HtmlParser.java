package cn.edu.sztui.base.domain.model.proxy.parser;

import lombok.extern.slf4j.Slf4j;
import org.jsoup.nodes.Document;
import org.springframework.stereotype.Component;


@Slf4j
@Component
public class HtmlParser {

    public String extractInputValue(Document doc, String inputName) {
        var element = doc.selectFirst("input[name=" + inputName + "]");
        return element != null ? element.val() : null;
    }
}
