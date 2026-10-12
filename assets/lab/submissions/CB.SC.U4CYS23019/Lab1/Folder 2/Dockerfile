 FROM busybox
RUN echo hello > /hello
RUN echo world > /hello
RUN touch remove_me /remove_me
ENV HELLO=jai
RUN rm /remove_me
