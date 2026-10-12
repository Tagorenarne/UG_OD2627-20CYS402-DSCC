FROM busybox
RUN echo hello > /hello
RUN echo world > /hello
RUN touch remove_me /remove_me
ENV HELLO=Martin
RUN rm /remove_me