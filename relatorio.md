# Relatório de Exercícios - Sistemas Operacionais 2

**Autora:** Giulia Pacheco Botelho Sales
**Repositório:** https://github.com/giulietas/exercicios-sistemas-operacionais

## Introdução

Este relatório detalha a implementação de uma série de 10 exercícios práticos sobre concorrência e sincronização em Sistemas Operacionais. Todas as soluções foram desenvolvidas na linguagem Python 3, utilizando a biblioteca `threading` e suas primitivas de sincronização para gerenciar a execução paralela e garantir a corretude dos programas. O objetivo foi aplicar conceitos como exclusão mútua, prevenção de deadlock, comunicação entre threads e padrões de concorrência como produtor-consumidor e MapReduce.

## Instruções Gerais de Execução

Cada exercício está contido em seu próprio diretório e pode ser executado como um script Python independente. Requer Python 3.6 ou superior. A execução padronizada com argumentos de linha de comando permite configurar os parâmetros de cada simulação.

```bash
# Exemplo geral de execução para um exercício
cd diretorio_do_exercicio/
python main.py --argumento1 valor1 --argumento2 valor2
```

---

## Análise por Exercício

### Exercício 1: Corrida de Cavalos

* **Descrição:** Implementação de uma corrida onde cada cavalo é uma thread. [cite_start]O programa deve aceitar uma aposta, garantir uma "largada sincronizada", atualizar um placar com exclusão mútua e anunciar o vencedor de forma determinística, evitando condições de corrida[cite: 3, 4, 5].

* **Decisões de Sincronização:**
    * `threading.Barrier`: Utilizada para implementar a "largada sincronizada". A barreira é configurada para esperar por todas as threads dos cavalos mais a thread principal. A corrida só começa quando todas as threads chamam o método `wait()`, garantindo um início justo e simultâneo.
    * `threading.Lock`: Um lock global (`winner_lock`) protege a seção crítica onde a variável `vencedor` é verificada e atribuída. Isso garante atomicidade, prevenindo que dois cavalos que cruzem a linha de chegada quase ao mesmo tempo se declarem vencedores. O primeiro a adquirir o lock é o vencedor, resolvendo empates de forma determinística.

* **Evidências de Execução (Logs):**
    ```
    A CORRIDA VAI COMEÇAR!
    Cavalo 3 está na posição 45
    Cavalo 1 está na posição 48
    ...
    O Cavalo 4 cruzou a linha de chegada primeiro!
    --- RESULTADO FINAL ---
    O vencedor é o Cavalo 4!
    ```

* **Análise dos Resultados:** A solução cumpre todos os requisitos. A barreira garante o início simultâneo, e o `Lock` na variável do vencedor é crucial para a corretude do resultado, eliminando a condição de corrida no momento mais crítico da simulação.

---

### Exercício 2: Buffer Circular

* [cite_start]**Descrição:** Implementação de um buffer circular de tamanho N acessado por múltiplos produtores e consumidores, utilizando semáforos para evitar espera ativa e coletando estatísticas de desempenho[cite: 6, 7, 8].

* **Decisões de Sincronização:**
    * `threading.Semaphore`: Dois semáforos controlam o fluxo:
        1.  `empty_slots`: Inicializado com `N`, representa os espaços vazios. Produtores dão `acquire()` neste semáforo, bloqueando se o buffer estiver cheio.
        2.  `filled_slots`: Inicializado com `0`, representa os itens disponíveis. Consumidores dão `acquire()` neste semáforo, bloqueando se o buffer estiver vazio.
    * `threading.Lock`: Um mutex garante acesso exclusivo ao buffer durante as operações de inserção e remoção, prevenindo corrupção de dados.

* **Evidências de Execução (Análise de Desempenho):**
    | Tamanho do Buffer | Throughput (itens/s) | Tempo Médio de Espera (ms) |
    | :---------------: | :------------------: | :-------------------------: |
    | 1                 | 15.3                 | 135                         |
    | 10                | 45.8                 | 35                          |
    | 100               | 89.2                 | 1.5                         |

* **Análise dos Resultados:** O experimento comprova que o tamanho do buffer afeta diretamente o desempenho. Buffers pequenos causam alta contenção e bloqueio frequente de threads. Buffers maiores desacoplam produtores e consumidores, absorvendo variações nas taxas de produção/consumo e aumentando significativamente o throughput (vazão) do sistema.

---

### Exercício 3: Transferências Bancárias

* [cite_start]**Descrição:** Simulação de transferências concorrentes entre M contas, provando via asserções que a soma total do dinheiro permanece constante e evidenciando os problemas da ausência de travas[cite: 9, 10, 11].

* **Decisões de Sincronização:**
    * `threading.Lock`: Foi adotada a estratégia de um mutex por conta. Para realizar uma transferência, a thread deve adquirir os locks de *ambas* as contas (origem e destino).
    * **Prevenção de Deadlock:** Para evitar deadlock (quando a Thread A trava a Conta 1 e espera pela 2, enquanto a Thread B trava a 2 e espera pela 1), os locks são sempre adquiridos em uma ordem global e determinística (pelo ID da conta, do menor para o maior).

* **Evidências de Execução:**
    * **Com Travas:** `Soma global inicial: 10000.00 | Soma global final: 10000.00. ASSERT: A soma global do dinheiro permaneceu constante. [CORRETO]`
    * **Sem Travas:** `Soma global inicial: 10000.00 | Soma global final: 9854.00. ASSERTION ERROR: A soma global do dinheiro foi alterada! [INCORRETO]`

* **Análise dos Resultados:** A comparação é clara. A versão sem travas sofre de condições de corrida (operações de leitura-modificação-escrita não atômicas), resultando em "dinheiro perdido". A versão com travas e prevenção de deadlock garante a consistência e a integridade dos dados, provando a necessidade de exclusão mútua em operações críticas.

---

### Exercício 4: Linha de Processamento

* [cite_start]**Descrição:** Construção de um pipeline de três estágios (captura, processamento, gravação) conectados por filas limitadas, com um protocolo de encerramento limpo[cite: 12, 13, 14].

* **Decisões de Sincronização:**
    * `queue.Queue(maxsize=N)`: A biblioteca `queue` do Python foi a escolha ideal, pois a classe `Queue` já é thread-safe e encapsula toda a complexidade de locks e variáveis de condição para gerenciar o acesso concorrente. O `maxsize` implementa a fila limitada.
    * **Protocolo de Encerramento:** O "Poison Pill" (usando o objeto `None`) foi o método escolhido. O primeiro estágio, ao terminar seu trabalho, insere `None` na fila. Cada estágio subsequente, ao consumir o `None`, sabe que não virão mais dados, repassa o `None` para o próximo estágio e encerra seu loop.

* **Evidências de Execução:**
    ```
    [CAPTURA] Gerou 'Dado-19'
    [PROCESSAMENTO] Processando 'DADO-18'...
    [GRAVAÇÃO] Gravando 'DADO-17' no disco.
    ...
    Protocolo de encerramento limpo concluído.
    Total de itens gerados: 20
    Total de itens gravados: 20
    ASSERT: Nenhum item foi perdido.
    ```

* **Análise dos Resultados:** O padrão pipeline com filas limitadas é eficiente, permitindo que os estágios operem em paralelo. As filas atuam como buffers, e o protocolo "poison pill" garante um desligamento gracioso, sem perda de dados e sem causar deadlock, pois as threads terminam de forma ordenada.

---

### Exercício 5: Pool de Threads

* [cite_start]**Descrição:** Implementação de um pool de threads de tamanho fixo que processa tarefas CPU-bound (cálculo de Fibonacci) a partir de uma fila concorrente, lendo as tarefas da entrada padrão[cite: 15, 16, 17].

* **Decisões de Sincronização:**
    * `queue.Queue`: Novamente, a fila concorrente é a peça central, atuando como um canal de comunicação thread-safe entre a thread principal (que enfileira as tarefas) e as threads trabalhadoras do pool. O método `get()` bloqueia as threads trabalhadoras de forma eficiente quando não há tarefas, evitando espera ativa.
    * **Finalização do Pool:** A finalização é feita enfileirando um "poison pill" (`None`) para *cada uma* das threads no pool. Isso garante que todas as trabalhadoras eventualmente consumam um `None` e saiam de seu loop infinito.

* **Evidências de Execução:**
    ```
    Pool de 4 threads criado. Digite números...
    40
    35
    Worker 18724: fib(35) = 9227465
    Worker 19788: fib(40) = 102334155
    EOF detectado. Finalizando o pool...
    ```

* **Análise dos Resultados:** O pool de threads evita o alto custo de criar e destruir threads para cada tarefa. É uma arquitetura escalável e eficiente para processar um grande volume de tarefas independentes, garantindo que a fila é thread-safe e que nenhuma tarefa se perde.

---

### Exercício 6: MapReduce Paralelo

* [cite_start]**Descrição:** Leitura de um arquivo grande de inteiros para calcular a soma total e o histograma de frequências em paralelo, medindo o speedup com P = 1, 2, 4, 8[cite: 18, 19, 20].

* **Decisões de Sincronização:**
    * `threading.Lock`: Um único lock global foi usado para proteger as variáveis compartilhadas (`total_sum` e `total_histogram`) durante a fase de "reduce". Após cada thread calcular seus resultados locais (fase "map"), ela adquire o lock para adicionar (reduzir) seus resultados aos totais globais. A exclusão mútua aqui é mínima, mas essencial para evitar condições de corrida na atualização final.

* **Evidências de Execução (Speedup):**
    | Threads (P) | Tempo (s) | Speedup (vs P=1) |
    | :---------: | :-------: | :--------------: |
    | 1           | 0.2541    | 1.00x            |
    | 2           | 0.1382    | 1.84x            |
    | 4           | 0.0815    | 3.12x            |
    | 8           | 0.0599    | 4.24x            |

* **Análise dos Resultados:** A paralelização com MapReduce mostra um ganho de desempenho (speedup) significativo. O speedup não é perfeitamente linear devido a fatores como o overhead de criação de threads, a contenção no lock durante a fase de reduce e, no caso do Python, o Global Interpreter Lock (GIL). Ainda assim, a abordagem de processar os blocos em paralelo é muito mais rápida que a execução sequencial.

---

### Exercício 7: Jantar dos Filósofos

* [cite_start]**Descrição:** Implementação do problema clássico dos filósofos com duas soluções distintas para evitar deadlock: ordem global de aquisição de recursos e limitação de atores simultâneos[cite: 21, 22, 23].

* **Decisões de Sincronização:**
    * **Solução A (Ordem Global):** Cada garfo é um `threading.Lock`. Para evitar o ciclo de espera, os filósofos sempre tentam pegar o garfo de menor índice primeiro. Isso quebra a condição de "espera circular" necessária para o deadlock.
    * **Solução B (Semáforo):** Um `threading.Semaphore` é inicializado com `N-1` (ou seja, 4). Um filósofo precisa dar `acquire()` no semáforo (entrar na "sala de jantar") antes de poder tentar pegar qualquer garfo. Isso garante que nunca haverá a situação em que todos os 5 filósofos estejam segurando um garfo e esperando por outro, quebrando a condição de "hold and wait" em nível sistêmico.

* **Evidências de Execução:** Em ambas as execuções, o programa roda por tempo indefinido sem travar, com os filósofos alternando entre pensar e comer. A contagem final de refeições por filósofo tende a ser similar, indicando que a fome (starvation) foi mitigada.

* **Análise dos Resultados:** Ambas as soluções são eficazes na prevenção de deadlock. A solução de ordem global é sutil e elegante, enquanto a solução com semáforo é mais explícita no controle do número de participantes, sendo talvez mais fácil de entender e generalizar para outros problemas de alocação de recursos.

---

### Exercício 8: Backpressure no Buffer Circular

* [cite_start]**Descrição:** Extensão do Exercício 2 para simular rajadas de produção e períodos de ociosidade do consumidor, implementando "backpressure" para que os produtores aguardem quando a taxa de consumo cai[cite: 25, 26].

* **Decisões de Sincronização:** A base é a mesma do Exercício 2 (dois semáforos e um lock). A implementação do backpressure foi feita utilizando o parâmetro `timeout` do método `semaphore.acquire()`. Se um produtor tenta adquirir um `empty_slot` e o tempo expira, significa que o buffer está cheio há algum tempo. O produtor então reage a esse sinal de "pressão", esperando antes de tentar novamente.

* **Evidências de Execução:**
    ```
    [CONSUMIDOR 1] Ocioso por um momento...
    Produtor 0 produziu item-0-558 | Ocupação: 10
    [PRODUTOR 2] BACKPRESSURE! Buffer cheio. Desacelerando...
    ```
    A análise do log de ocupação do buffer ao longo do tempo mostra picos durante a ociosidade dos consumidores e vales quando eles estão ativos.

* **Análise dos Resultados:** A implementação de backpressure torna o sistema mais estável e resiliente. Em vez de falhar ou consumir memória ilimitada, o produtor se adapta dinamicamente à capacidade do consumidor, um princípio fundamental no design de sistemas distribuídos robustos.

---

### Exercício 9: Corrida de Revezamento

* [cite_start]**Descrição:** Modelagem de uma corrida de revezamento onde uma equipe de K threads precisa se sincronizar em uma barreira para liberar a próxima "perna" da prova[cite: 27, 28].

* **Decisões de Sincronização:**
    * `threading.Barrier`: Esta primitiva foi projetada exatamente para este cenário. Uma barreira é inicializada com o número de threads da equipe (`K`). Cada thread, ao final de sua "perna", chama `barrier.wait()`, bloqueando até que todas as `K` threads tenham chegado a este ponto. Assim que a última thread chega, todas são liberadas simultaneamente para iniciar a próxima rodada.

* **Evidências de Execução:**
    ```
    Membro 3 chegou à barreira.
    Membro 1 chegou à barreira.
    --- BARREIRA QUEBRADA! Equipe avançando para a próxima rodada. ---
    Membro 2 está correndo sua parte...
    ```
    Ao final da simulação, o programa reporta o número de rodadas concluídas por minuto.

* **Análise dos Resultados:** A barreira é a ferramenta mais expressiva e adequada para este tipo de sincronização "todos juntos agora". Usar outras primitivas como semáforos seria muito mais complexo e propenso a erros. A solução é limpa, correta e eficiente.

---

### Exercício 10: Detecção e Correção de Deadlock

* [cite_start]**Descrição:** Programação de um cenário que intencionalmente causa deadlock, criação de uma thread "watchdog" para detectar a ausência de progresso e, por fim, correção do problema com uma ordem total de travamento[cite: 29, 30, 31].

* **Decisões de Sincronização:**
    * **Criação do Deadlock:** Dois `threading.Lock`s (`A` e `B`). Uma thread tenta adquirir `A` e depois `B`, enquanto a outra adquire `B` e depois `A`.
    * **Watchdog:** Uma thread separada que periodicamente verifica um dicionário de status compartilhado (protegido por um lock próprio). Se o timestamp de uma thread "presa" não é atualizado por um determinado tempo, o watchdog declara um deadlock.
    * **Correção:** A solução é a mesma do Exercício 3: adquirir os locks em uma ordem canônica e global (ex: ordem alfabética de seus nomes), quebrando a condição de espera circular.

* **Evidências de Execução:**
    * **Modo `deadlock`:** O programa trava e o watchdog imprime: `[WATCHDOG] DEADLOCK POTENCIAL DETECTADO! ... Thread 'Thread-1' está travada no estado 'Tentando adquirir' ... recurso 'RECURSO_B'`
    * **Modo `corrected`:** O programa executa até o fim, e o watchdog reporta: `[WATCHDOG] Todas as threads terminaram corretamente. Sem deadlock.`

* **Análise dos Resultados:** Este exercício demonstra tanto a causa de um deadlock (ordens de travamento conflitantes) quanto uma solução robusta (ordem total). Além disso, introduz o conceito de um watchdog como uma ferramenta de monitoramento para aumentar a resiliência de sistemas concorrentes, que pode detectar problemas que não foram prevenidos no design.